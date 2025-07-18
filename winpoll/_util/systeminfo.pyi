from ctypes import c_void_p
from typing import Set, TypedDict

class _SystemInfo(TypedDict):
    pageSize: int
    minimumApplicationAddress: c_void_p
    maximumApplicationAddress: c_void_p
    activeProcessorMask: int
    _activeProcessors: Set[int]
    numberOfProcessors: int
    allocationGranularity: int
    processorLevel: int
    processorRevision: int
    processorArchitecture: int
    oemId: int

def getpagesize() -> int: ...
def getallocationgranularity() -> int: ...
def GetSystemInfo() -> _SystemInfo: ...
