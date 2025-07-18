Implementation of `select.poll` on Microsoft Windows.

- Pure Python; no C extensions (uses `ctypes.windll`)
- Drop-in-compatible API
- Clean "ponyfill"; no monkeypatching
- No dependencies (besides Windows Vista or newer)
- Python 3.6+ compatible


# Usage

```python
try:
  from select import POLLIN, POLLOUT, poll
except ImportError:
  # https://github.com/python/cpython/issues/60711
  from winpoll import POLLIN, POLLOUT, wsapoll as poll

p = poll()

p.register(sock1, POLLIN)
p.register(sock2, POLLIN | POLLOUT)
p.unregister(sock1)

for sock, events in p.poll(timeout=3):
    print(f"Socket {sock} is ready with {events}")

# like select.poll objects, winpoll.wsapoll objects acquire no resources
# thus have no cleanup requirement besides plain garbage collection
```


# Limitations / Bugs

- Does not work before Windows Vista.

  * Last affected OS EOL: [April 8, 2014](https://learn.microsoft.com/en-us/lifecycle/announcements/windows-xp-office-exchange-2003-end-of-support)

- Outbound TCP connections don't correctly report failure-to-connect (`(POLLHUP | POLLERR | POLLWRNORM)`) before Windows 10 Version 2004 (OS build 19041).

  * Last affected OS EOL: [May 10, 2022](https://learn.microsoft.com/en-us/lifecycle/announcements/windows-10-1909-enterprise-education-eos)


# Installation

## Command-line

```cmd
pip install winpoll
```

## `requirements.txt`

```ini
winpoll
```

## `pyproject.toml`

```toml
[project]
dependencies = [
  ...,
  "winpoll",
]
```
