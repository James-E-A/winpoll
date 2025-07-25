from ctypes import WinError, byref, create_string_buffer, memmove, resize, sizeof
from ctypes import windll
from ctypes.wintypes import INT, LPVOID, ULONG
from errno import ENOENT
import logging
from selectors import _PollLikeSelector
from socket import SOCK_STREAM, socket as socket_
import sys
from threading import Lock
from time import monotonic_ns

from ._util.select_extra import *
from ._util import (
    POLL_FLAGS_FOR_REPR,
    SOCKET_ERROR,
    WSAEINTR,
    WSAPOLLFD,
    enter_or_die,
    getallocationgranularity,
    getfd,
    repr_flags,
    smallest_multiple_atleast,
    uptruncate,
)

__all__ = [
    'POLLERR',
    'POLLHUP',
    'POLLIN',
    'POLLNVAL',
    'POLLOUT',
    'POLLPRI',
    'POLLRDBAND',
    'POLLRDNORM',
    'POLLWRBAND',
    'POLLWRNORM',
    'wsapoll',
    'WSAPollSelector',
]

IS_PRE_19041 = sys.getwindowsversion() < (10, 0, 19041)
_POLL_DISCONNECTION = POLLHUP | POLLERR | POLLWRNORM


_WSAPoll = windll.Ws2_32['WSAPoll']

_WSAPoll.argtypes = [
    LPVOID,
    ULONG,
    INT,
]


_WSAGetLastError = windll.Ws2_32['WSAGetLastError']


class wsapoll:
    __slots__ = [
        '_registered',
        '__impl',
        '__impl_uptodate',
        # We have to track the buffer separately to avoid freaking ctypes out
        # if resize is called more than once; only the originally allocated
        # object "owns" the memory, even after a call to resize. There is no way
        # to robustly resize ctypes.Array instances at this time, so we are
        # just keeping the original buffer around, in addition to impl, which
        # is a subordinate "view" of only the buffer's allocated slots.
        # https://github.com/python/cpython/issues/65527
        # https://docs.python.org/3/library/ctypes.html#ctypes._CData._b_needsfree_
        '__buffer',
        # https://github.com/python/cpython/blob/v3.13.0/Modules/selectmodule.c#L661-L666
        # https://github.com/pypy/pypy/blob/release-pypy3.11-v7.3.18/pypy/module/select/interp_select.py#L87-L88
        '__lock',
        # https://docs.python.org/3/library/weakref.html#:~:text=When%20__slots__%20are%20defined%20for%20a%20given%20type,declaration%2E
        '__weakref__',
    ]

    def __init__(self, sizehint=max(getallocationgranularity() // sizeof(WSAPOLLFD), 1)):
        self._registered = {}
        impl_t = WSAPOLLFD * 0
        self.__buffer = buf = (impl_t._type_ * sizehint)()
        self.__impl = impl_t.from_buffer(buf)
        self.__impl_uptodate = True
        self.__lock = Lock()

    def __repr__(self):
        return f"<{__name__}.{self.__class__.__name__} _registrations={{{', '.join(f'{fd!r}: {repr_flags(eventmask, POLL_FLAGS_FOR_REPR)}' for fd, eventmask in self._registered.items())}}}>"

    def __check_maybe_affected(self):
        return any(
            (
                fd >= 0
                and eventmask == _POLL_DISCONNECTION
            )
            for fd, eventmask in self._registered.items()
        )

    def poll(self, timeout=None):
        with enter_or_die(self.__lock, "concurrent poll() invocation"):
            if IS_PRE_19041 and (timeout is None) and self.__check_maybe_affected():
                logging.warning("Outbound TCP connection failures won't be reported by wsapoll.poll() on versions of Windows prior to \"Windows 10 version 2004 (OS build 19041)\"; consider updating the operating system, using IOCP (via asyncio), or setting a finite timeout.\nFor more information, see https://daniel.haxx.se/blog/2012/10/10/wsapoll-is-broken/")

            if not self.__impl_uptodate:
                self.__update_impl()

            timeout_ms = uptruncate(timeout * 1000) if timeout is not None else -1
            return self._poll(timeout_ms)

    def _poll(self, timeout=-1):
        impl = self.__impl
        impl_len = len(impl)

        # https://github.com/python/cpython/blob/v3.13.0/Modules/selectmodule.c#L645-L647
        if timeout >= 0:
            timeout_deadline = monotonic_ns() // 1000 + timeout

        # https://github.com/python/cpython/blob/v3.13.0/Modules/selectmodule.c#L675-L701
        while True:
            # no need to call "byref" as that's already how ctypes handles arrays passed as LPVOID
            ret = _WSAPoll(impl, impl_len, timeout)

            # https://learn.microsoft.com/en-us/windows/win32/api/winsock2/nf-winsock2-wsapoll#return-value
            if ret == SOCKET_ERROR:
                errno = _WSAGetLastError()

                # https://peps.python.org/pep-0475/
                if errno == WSAEINTR:
                    # https://github.com/python/cpython/blob/v3.13.0/Modules/selectmodule.c#L692-L699
                    if timeout >= 0:
                        timeout = max(timeout_deadline - monotonic_ns() // 1000, 0)
                    continue

                raise WinError(errno)

            assert 0 <= ret <= impl_len
            break

        return [
            (fd, events)
            for fd, events in ((slot.fd, slot.revents) for slot in impl)
                if events
        ]

    def __update_impl(self):
        registered = self._registered
        impl = self.__impl
        buf = self.__buffer

        fds = len(registered)
        impl_t = impl._type_ * fds

        if sizeof(impl_t) > sizeof(buf):
            # ...But first, actually purchase moar RAM
            resize(
                buf,
                smallest_multiple_atleast(
                    getallocationgranularity(),
                    max(
                        sizeof(impl._type_ * (len(impl) * 2)),
                        sizeof(impl_t)
                    )
                )
            )

        self.__impl = impl = impl_t.from_buffer(buf)

        for slot, (fd, eventmask) in zip(impl, registered.items()):
            slot.fd = fd
            slot.events = eventmask

        self.__impl_uptodate = True

    def register(self, fd, eventmask=(POLLIN | POLLPRI | POLLOUT)):
        fd_ = getfd(fd)
        with self.__lock:
            self._registered[fd_] = eventmask

            self.__impl_uptodate = False

    def unregister(self, fd):
        fd_ = getfd(fd)
        with self.__lock:
            try:
                del self._registered[fd_]
            except KeyError:
                raise KeyError(f"{fd!r} is not registered") from None

            self.__impl_uptodate = False

    def modify(self, fd, eventmask):
        fd_ = getfd(fd)
        with self.__lock:
            try:
                self._registered[fd_]
            except KeyError:
                # https://github.com/python/cpython/blob/v3.13.0/Modules/selectmodule.c#L548
                raise OSError(ENOENT, f"{fd!r} is not registered") from None
            else:
                self._registered[fd_] = eventmask

            self.__impl_uptodate = False

    def _clear(self):
        with self.__lock:
            self._registered.clear()
            self.__update_impl()

    def __getstate__(self):
        return self._registered.copy()

    def __setstate__(self, state):
        self.__init__(sizehint=len(state))
        self._registered.update(state)
        self.__update_impl()


# https://github.com/python/cpython/blob/v3.13.0/Lib/selectors.py#L412-L418
class WSAPollSelector(_PollLikeSelector):
    """WSAPoll-based selector."""
    _selector_cls = wsapoll
    _EVENT_READ = POLLIN
    _EVENT_WRITE = POLLOUT
