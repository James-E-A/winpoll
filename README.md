Implementation of `select.poll` on Microsoft Windows.

- Pure Python; no C extensions (uses `ctypes.windll.Ws2_32`)
- Drop-in-compatible API
- Clean "ponyfill"; library does no monkeypatching
- No dependencies (besides Windows Vista or newer)
- Python 3.6+ compatible


# Usage

## Alternative to `select.poll`

```python
try:
    from select import (
        POLLIN, POLLOUT, POLLERR, POLLHUP, POLLNVAL,
        poll
    )

except ImportError:
    # https://github.com/python/cpython/issues/60711
    from winpoll import (
        POLLIN, POLLOUT, POLLERR, POLLHUP, POLLNVAL,
        wsapoll as poll
    )
```

```python
p = poll()

p.register(sock1, POLLIN)
p.register(sock2, POLLIN | POLLOUT)
p.unregister(sock1)

for fd, events in p.poll(3):
    print(f"<socket.socket fd={fd}> is ready with {events}")
```

Like `select.poll`, `winpoll.wsapoll` objects acquire no special resources, thus
have no cleanup requirement (besides plain garbage collection).

## Alternative to `selectors.PollSelector`/`selectors.DefaultSelector`

```python
import sys
from selectors import (
    EVENT_READ, EVENT_WRITE,
    DefaultSelector, SelectSelector
)

if (DefaultSelector is SelectSelector) and (sys.platform == 'win32') and (sys.getwindowsversion() >= (10, 0, 19041)):
    # https://github.com/python/cpython/issues/60711
    from winpoll import WSAPollSelector as DefaultSelector
```

```python
s = DefaultSelector()

s.register(sock1, EVENT_READ)
s.register(sock2, EVENT_READ | EVENT_WRITE)
s.unregister(sock1)

for (sock, _fd, _eventmask, _data), events in s.select(3):
    print(f"{sock} is ready with {events}")
```


# Limitations / Bugs

- Does not work before Windows Vista.

  * Last affected OS EOL: [April 8, 2014](https://learn.microsoft.com/en-us/lifecycle/announcements/windows-xp-office-exchange-2003-end-of-support)

- Outbound TCP connections don't correctly report failure-to-connect (`(POLLHUP | POLLERR | POLLWRNORM)`) before Windows 10 Version 2004 (OS build 19041).

  * Last affected OS EOL: [May 10, 2022](https://learn.microsoft.com/en-us/lifecycle/announcements/windows-10-1909-enterprise-education-eos)


# Installation

## Command-line

```cmd
pip install "winpoll ; sys_platform == 'win32'"
```

## `requirements.txt`

```ini
winpoll ; sys_platform == 'win32'
```

## `pyproject.toml`

```toml
[project]
dependencies = [
  ...,
  "winpoll ; sys_platform == 'win32'",
]
```
