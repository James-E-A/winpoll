import ctypes
from ctypes import POINTER, c_void_p
from ctypes import oledll, wintypes
from ctypes.wintypes import DWORD, WORD, LPVOID
from functools import cache

from .wintypes_extra import DWORD_PTR

__all__ = [
    'getpagesize',
    'getallocationgranularity',
    'GetSystemInfo',
]


@cache
def getpagesize():
    return GetSystemInfo()['pageSize']

@cache
def getallocationgranularity():
    return GetSystemInfo()['allocationGranularity']


class SYSTEM_INFO(ctypes.Structure):
    class _field_1(ctypes.Union):
        class _field_2(ctypes.Structure):
            _fields_ = [
                ('wProcessorArchitecture', WORD),
                ('wReserved', WORD),
            ]
        _anonymous_ = ['_2']
        _fields_ = [
            ('dwOemId', DWORD),
            ('_2', _field_2),
        ]
    _anonymous_ = ['_1']
    _fields_ = [
        ('_1', _field_1),
        ('dwPageSize', DWORD),
        ('lpMinimumApplicationAddress', LPVOID),
        ('lpMaximumApplicationAddress', LPVOID),
        ('dwActiveProcessorMask', DWORD_PTR),
        ('dwNumberOfProcessors', DWORD),
        ('dwProcessorType', DWORD),
        ('dwAllocationGranularity', DWORD),
        ('wProcessorLevel', WORD),
        ('wProcessorRevision', WORD),
    ]

    @property
    def value(self):
        return {
            'pageSize': self.dwPageSize,
            'minimumApplicationAddress': c_void_p(self.lpMinimumApplicationAddress),
            'maximumApplicationAddress': c_void_p(self.lpMaximumApplicationAddress),
            'activeProcessorMask': self.dwActiveProcessorMask,
            '_activeProcessors': frozenset((lambda mask, n: (i for i in range(n) if (mask & (1<<i))))(self.dwActiveProcessorMask, self.dwNumberOfProcessors)),
            'numberOfProcessors': self.dwNumberOfProcessors,
            'allocationGranularity': self.dwAllocationGranularity,
            'processorLevel': self.wProcessorLevel,
            'processorRevision': self.wProcessorRevision,
            'processorArchitecture': self.wProcessorArchitecture,
            'oemId': self.dwOemId
        }


_GetNativeSystemInfo = oledll.Kernel32['GetNativeSystemInfo']

_GetNativeSystemInfo.argtypes = [
    POINTER(SYSTEM_INFO),
]


def GetSystemInfo():
    result = SYSTEM_INFO()
    _GetNativeSystemInfo(result)
    return result.value
