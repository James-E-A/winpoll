from ctypes import Array as ctypes_Array
from _ctypes import _CData
from collections.abc import MutableMapping
from numbers import Real
from threading import Lock
from typing import List, Optional, Protocol, Tuple, Union

from ._util.wintypes_extra import WSAPOLLFD

POLLERR: int
POLLHUP: int
POLLIN: int
POLLNVAL: int
POLLOUT: int
POLLPRI: int
POLLRDBAND: int
POLLRDNORM: int
POLLWRBAND: int
POLLWRNORM: int

class _Fileobj(Protocol):
    def fileno(self) -> int: ...

class wsapoll:
    __slots__ = ['__impl', '__fd_to_key', '__buffer']
    _registered: MutableMapping[int, int]
    __impl: ctypes_Array[WSAPOLLFD]
    __impl_uptodate: bool
    __buffer: _CData
    __lock: Lock
    def __init__(self, sizehint: int=...) -> None: ...
    def __repr__(self) -> str: ...

    def register(self, fd: Union[_Fileobj, int], eventmask: int=...) -> None: ...
    def modify(self, fd: Union[_Fileobj, int], eventmask: int) -> None: ...
    def unregister(self, fd: Union[_Fileobj, int]) -> None: ...
    def poll(self, timeout: Optional[Real]=None) -> List[Tuple[int, int]]: ...

    def _poll(self, timeout: int=-1) -> List[Tuple[int, int]]: ...
    def _clear(self) -> None: ...
    def __check_maybe_affected(self) -> bool: ...
    def __update_impl(self) -> None: ...
