import select

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
]


# https://github.com/wine-mirror/wine/blob/wine-10.12/include/winsock2.h#L325
try: POLLERR = select.POLLERR
except AttributeError: POLLERR = 0x0001

# https://github.com/wine-mirror/wine/blob/wine-10.12/include/winsock2.h#L326
try: POLLHUP = select.POLLHUP
except AttributeError: POLLHUP = 0x0002

# https://github.com/wine-mirror/wine/blob/wine-10.12/include/winsock2.h#L327
try: POLLNVAL = select.POLLNVAL
except AttributeError: POLLNVAL = 0x0004

# https://github.com/wine-mirror/wine/blob/wine-10.12/include/winsock2.h#L328
try: POLLWRNORM = select.POLLWRNORM
except AttributeError: POLLWRNORM = 0x0010

# https://github.com/wine-mirror/wine/blob/wine-10.12/include/winsock2.h#L329
try: POLLWRBAND = select.POLLWRBAND
except AttributeError: POLLWRBAND = 0x0020

# https://github.com/wine-mirror/wine/blob/wine-10.12/include/winsock2.h#L330
try: POLLRDNORM = select.POLLRDNORM
except AttributeError: POLLRDNORM = 0x0100

# https://github.com/wine-mirror/wine/blob/wine-10.12/include/winsock2.h#L331
try: POLLRDBAND = select.POLLRDBAND
except AttributeError: POLLRDBAND = 0x0200

# https://github.com/wine-mirror/wine/blob/wine-10.12/include/winsock2.h#L332
try: POLLPRI = select.POLLPRI
except AttributeError: POLLPRI = 0x0400

# https://github.com/wine-mirror/wine/blob/wine-10.12/include/winsock2.h#L333
try: POLLIN = select.POLLIN
except AttributeError: POLLIN = (POLLRDNORM | POLLRDBAND)

# https://github.com/wine-mirror/wine/blob/wine-10.12/include/winsock2.h#L334
try: POLLOUT = select.POLLOUT
except AttributeError: POLLOUT = POLLWRNORM
