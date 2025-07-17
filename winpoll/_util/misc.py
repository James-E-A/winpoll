from math import ceil, floor

from .select_extra import *

__all__ = [
    'POLL_FLAGS_FOR_REPR',
    'getfd',
    'repr_flags',
    'smallest_multiple_atleast',
    'uptruncate',
]


POLL_FLAGS_FOR_REPR = {
    'POLLIN': POLLIN, # prefer reporting semantic POLLIN over its components, when applicable
    'POLLRDNORM': POLLRDNORM,
    'POLLRDBAND': POLLRDBAND,
    'POLLPRI': POLLPRI,
    'POLLOUT': POLLOUT, # prefer reporting semantic POLLOUT over its components, when applicable
    'POLLWRNORM': POLLWRNORM,
    'POLLWRBAND': POLLWRBAND,
    'POLLERR': POLLERR,
    'POLLHUP': POLLHUP,
    'POLLNVAL': POLLNVAL,
}


def getfd(fileobj):
    return int(fileobj.fileno()) if hasattr(fileobj, 'fileno') else index(fileobj)


def uptruncate(x):
    "cast float *x* to an integer, rounding away from zero."
    if not (x < 0.0):
        return ceil(x)
    else:
        return floor(x)


def smallest_multiple_atleast(base, minimum_value):
    "return the smallest multiple of *base* less than *minimum_value*."
    return base * ((minimum_value + base - 1) // base)


def repr_flags(mask, flags):
    acc1 = int(mask)
    acc2 = []

    for name, value in flags.items():
        if (acc1 & value) == value:
            acc1 &= ~value
            acc2.append(name)

    if acc1 != 0 or len(acc2) == 0:
        acc2.append(str(acc1))
    
    if len(acc2) == 1:
        return acc2[0]

    return f"({' | '.join(acc2)})"
