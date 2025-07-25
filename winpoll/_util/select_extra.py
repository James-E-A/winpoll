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


# https://github.com/wine-mirror/wine/blob/wine-10.12/include/winsock2.h#L314
try: POLLERR = select.POLLERR
except AttributeError: POLLERR = 0x0001

# https://github.com/wine-mirror/wine/blob/wine-10.12/include/winsock2.h#L315
try: POLLHUP = select.POLLHUP
except AttributeError: POLLHUP = 0x0002

# https://github.com/wine-mirror/wine/blob/wine-10.12/include/winsock2.h#L316
try: POLLNVAL = select.POLLNVAL
except AttributeError: POLLNVAL = 0x0004

# https://github.com/wine-mirror/wine/blob/wine-10.12/include/winsock2.h#L317
try: POLLWRNORM = select.POLLWRNORM
except AttributeError: POLLWRNORM = 0x0010

# https://github.com/wine-mirror/wine/blob/wine-10.12/include/winsock2.h#L318
try: POLLWRBAND = select.POLLWRBAND
except AttributeError: POLLWRBAND = 0x0020

# https://github.com/wine-mirror/wine/blob/wine-10.12/include/winsock2.h#L319
try: POLLRDNORM = select.POLLRDNORM
except AttributeError: POLLRDNORM = 0x0100

# https://github.com/wine-mirror/wine/blob/wine-10.12/include/winsock2.h#L320
try: POLLRDBAND = select.POLLRDBAND
except AttributeError: POLLRDBAND = 0x0200

# https://github.com/wine-mirror/wine/blob/wine-10.12/include/winsock2.h#L321
try: POLLPRI = select.POLLPRI
except AttributeError: POLLPRI = 0x0400

# https://github.com/wine-mirror/wine/blob/wine-10.12/include/winsock2.h#L322
try: POLLIN = select.POLLIN
except AttributeError: POLLIN = (POLLRDNORM | POLLRDBAND)

# https://github.com/wine-mirror/wine/blob/wine-10.12/include/winsock2.h#L323
try: POLLOUT = select.POLLOUT
except AttributeError: POLLOUT = POLLWRNORM
