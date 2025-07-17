import ctypes
from ctypes import wintypes
from ctypes.wintypes import DWORD, SHORT

from .misc import POLL_FLAGS_FOR_REPR, repr_flags

__all__ = [
    'DWORD_PTR',
    'INVALID_SOCKET',
    'SOCKET',
    'SOCKET_ERROR',
    'UINT_PTR',
    'WSAEINTR',
    'WSAEINVAL',
    'WSAPOLLFD',
]


try: UINT_PTR = wintypes.UINT_PTR
except AttributeError: UINT_PTR = ctypes.c_size_t

try: DWORD_PTR = wintypes.DWORD_PTR
except AttributeError: DWORD_PTR = max([DWORD, UINT_PTR], key=ctypes.sizeof)


# https://github.com/wine-mirror/wine/blob/wine-10.12/include/winsock2.h#L139
try: SOCKET = wintypes.SOCKET
except AttributeError: SOCKET = UINT_PTR

# https://github.com/wine-mirror/wine/blob/wine-10.12/include/winsock2.h#L166
try: INVALID_SOCKET = wintypes.INVALID_SOCKET
except AttributeError: INVALID_SOCKET = SOCKET(~0).value

# https://github.com/wine-mirror/wine/blob/wine-10.12/include/winsock2.h#L167
try: SOCKET_ERROR = wintypes.SOCKET_ERROR
except AttributeError: SOCKET_ERROR = -1


# https://learn.microsoft.com/en-us/windows/win32/winsock/windows-sockets-error-codes-2#WSAEINTR
try: WSAEINTR = wintypes.WSAEINTR
except AttributeError: WSAEINTR = 10004

# https://learn.microsoft.com/en-us/windows/win32/winsock/windows-sockets-error-codes-2#WSAEINVAL
try: WSAEINVAL = wintypes.WSAEINVAL
except AttributeError: WSAEINVAL = 10022


_SSOCKET = {
    ctypes.c_uint64: ctypes.c_int64,
    ctypes.c_int64:  ctypes.c_int64,
    ctypes.c_uint32: ctypes.c_int32,
    ctypes.c_int32:  ctypes.c_int32,
    ctypes.c_uint16: ctypes.c_int16,
    ctypes.c_int16:  ctypes.c_int16,
    ctypes.c_uint8:  ctypes.c_int8,
    ctypes.c_int8:   ctypes.c_int8,
}[SOCKET]


class WSAPOLLFD(ctypes.Structure):
    __slots__ = []
    class _field_1(ctypes.Union):
        __slots__ = []
        _fields_ = [
            ('fd', SOCKET), # regular access in accordance with the "official" struct definition
            ('_fd', _SSOCKET), # signed access to reliably determine which fields "are negative" thus WSAPoll will ignore
        ]
    _anonymous_ = ['_1']
    _fields_ = [
        ('_1', _field_1),
        ('events', SHORT),
        ('revents', SHORT),
    ]

    def __init__(self, fd=INVALID_SOCKET, events=0, revents=0):
        self.fd = fd
        self.events = events
        self.revents = revents

    def __repr__(self):
        if self.fd != INVALID_SOCKET:
            return f"<{__name__}.{self.__class__.__name__} fd={self.fd}, events={repr_flags(self.events, POLL_FLAGS_FOR_REPR)}, revents={repr_flags(self.revents, POLL_FLAGS_FOR_REPR)}>"
        else:
            return f"<{__name__}.{self.__class__.__name__} fd=INVALID_SOCKET, ...>"
