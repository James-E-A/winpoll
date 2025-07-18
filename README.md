Implementation of `select.poll` on Microsoft Windows.

- Pure Python; no C extensions (uses `ctypes.windll.Ws2_32`)
- Drop-in-compatible API
- Clean "ponyfill"; no monkeypatching
- No dependencies (besides Windows Vista or newer)
- Python 3.6+ compatible


# Usage

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

for sock, events in p.poll(timeout=3):
    print(f"Socket {sock} is ready with {events}")
```

Like `select.poll`, `winpoll.wsapoll` objects acquire no special resources, thus
have no cleanup requirement (besides plain garbage collection).


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
