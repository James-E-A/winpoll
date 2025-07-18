Implementation of `select.poll` for Windows.

- Pure Python
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

# wsapoll objects acquire no resources and have no cleanup requirement
# besides plain garbage collection
```


# Limitations / Bugs

- Does not work before Windows Vista.

  * Last affected OS EOL: [April 8, 2014](https://learn.microsoft.com/en-us/lifecycle/announcements/windows-xp-office-exchange-2003-end-of-support)

- Outbound TCP connections don't correctly report failure-to-connect (`(POLLHUP | POLLERR)`) before Windows 10 Version 2004 (OS build 19041).

  * Last affected OS EOL: [May 10, 2022](https://learn.microsoft.com/en-us/lifecycle/announcements/windows-10-1909-enterprise-education-eos)
