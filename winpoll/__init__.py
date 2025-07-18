from ctypes import WinError, byref, create_string_buffer, memmove, resize, sizeof
from ctypes import windll
from ctypes.wintypes import INT, LPVOID, ULONG
from time import monotonic_ns

from ._util.select_extra import *
from ._util import (
    POLL_FLAGS_FOR_REPR,
    SOCKET_ERROR,
    WSAEINTR,
    WSAPOLLFD,
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
]


_WSAPoll = windll.Ws2_32['WSAPoll']

_WSAPoll.argtypes = [
    LPVOID,
    ULONG,
    INT,
]


_WSAGetLastError = windll.Ws2_32['WSAGetLastError']


class wsapoll:
    __slots__ = [
        '__impl',
        '__fd_to_key',
        # We have to track the buffer separately to avoid freaking ctypes out
        # if resize is called more than once; only the originally allocated
        # object "owns" the memory, even after a call to resize. There is no way
        # to robustly resize ctypes.Array instances at this time, so we are
        # just keeping the original buffer around, in addition to impl, which
        # is a subordinate "view" of only its active slots.
        # https://github.com/python/cpython/issues/65527
        # https://docs.python.org/3/library/ctypes.html#ctypes._CData._b_needsfree_
        '__buffer',
    ]

    def __init__(self, sizehint=max(getallocationgranularity() // sizeof(WSAPOLLFD), 1)):
        impl_t = WSAPOLLFD * 0
        self.__buffer = buf = (impl_t._type_ * sizehint)()
        self.__impl = impl_t.from_buffer(buf)
        self.__fd_to_key = {}

    def __repr__(self):
        return f"<{__name__}.{self.__class__.__name__} {{{', '.join(f'{fd}: {repr_flags(events, POLL_FLAGS_FOR_REPR)}' for fd, events in ((slot._fd, slot.events) for slot in self.__impl ) )}}}>"

    def _check(self):
        set_1 = set(slot.fd for slot in self.__impl)
        set_2 = set(self.__fd_to_key.keys())
        if set_1 != set_2:
            raise AssertionError(f"internal inconsistency: descriptors {set_2} were registered, but only {set_1} were present in the struct")

    def poll(self, timeout=None):
        timeout_ms = uptruncate(timeout * 1000) if timeout is not None else -1
        return self._poll(timeout_ms)

    def _poll(self, timeout=-1):
        impl = self.__impl
        fd_to_key = self.__fd_to_key
        impl_len = len(impl)

        # https://github.com/python/cpython/blob/v3.13.0/Modules/selectmodule.c#L661-L666
        # FIXME: raise if called concurrently on the same thread

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

            assert 0 <= ret <= len(fd_to_key)
            break

        fd_to_key_getitem = fd_to_key.__getitem__

        return [
            (fd_to_key_getitem(fd), events)
            for fd, events in ((slot.fd, slot.revents) for slot in impl)
                if events != 0
        ]

    def register(self, fileobj, eventmask=(POLLIN | POLLPRI | POLLOUT)):
        fd = getfd(fileobj)
        impl = self.__impl
        fd_to_key = self.__fd_to_key

        # 1. Find existing slot for this FD
        for slot in impl:
            if slot.fd == fd:
                # 2A. Found the slot to update this existing fd registration
                break

        # 2. If none found, bump-alloc new slot by updating array metadata
        else:
            buf = self.__buffer
            impl_t = impl._type_ * (len(impl) + 1)

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
            slot = impl[-1]

        # 3. Set slot contents
        slot.fd = fd
        slot.events = eventmask

        # 4. Update (remaining) registration metadata
        fd_to_key[fd] = fileobj

        if __debug__: self._check()

    def modify(self, fileobj, eventmask):
        fd = getfd(fileobj)

        # 1. Find slot for this fd
        for slot in self.__impl:
            if slot.fd == fd:
                break
        else:
            raise KeyError(f"{fileobj!r} is not registered")

        # 2. Update slot contents
        slot.events = eventmask

        # 3. Update registration metadata
        self.__fd_to_key[fd] = fileobj

        if __debug__: self._check()

    def _clear(self):
        impl_t = self.__impl._type_ * 0
        self.__impl = impl_t.from_buffer(self.__buffer)
        self.__fd_to_key.clear()

        if __debug__: self._check()

    def unregister(self, fileobj):
        fd = getfd(fileobj)
        impl = self.__impl

        # 1. Find slot for this fd
        for (i, slot) in enumerate(impl):
            if slot.fd == fd:
                count_after = len(impl) - i - 1
                break
        else:
            raise KeyError(f"{fileobj!r} is not registered")

        # 2. Update slot contents, if applicable
        if count_after > 0:
            memmove(
                byref(slot),
                byref(slot, sizeof(slot)),
                sizeof(slot) * count_after
            )

        # 3. Update registration metadata
        impl_t = impl._type_ * (len(impl) - 1)
        self.__impl = impl_t.from_buffer(self.__buffer)
        del self.__fd_to_key[fd]

        if __debug__: self._check()
