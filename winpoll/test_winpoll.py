import winpoll

import contextlib
import time
import socket
import unittest

UNDERSLEEP_TOLERANCE_NS = 0  # zero-tolerance
OVERSLEEP_TOLERANCE_NS = 50_000_000  # 50 milliseconds


def _churn_fds(minimum=1024):
    deadline_ns = time.monotonic_ns() + 10_000_000_000  # 10 seconds
    while True:
        with contextlib.ExitStack() as stack:
            socks = [stack.enter_context(sock) for sock in socket.socketpair()]

            if any(sock.fileno() > minimum for sock in socks):
                return

            if time.monotonic_ns() > deadline_ns:
                raise RuntimeError(f"failed to reach target minimum fd")


class TestWsaPoll(unittest.TestCase):
    def test_pollout(self):
        obj = winpoll.wsapoll()

        with contextlib.ExitStack() as stack:
            sock1, sock2 = map(stack.enter_context, socket.socketpair())
            obj.register(sock1, winpoll.POLLOUT)

            result = obj.poll()

            self.assertEqual(len(result), 1)
            # !!!!!FIXME!!!!! don't run the following code if the preceding test failed
            result_fd, result_events = result[0]
            self.assertEqual(result_fd, sock1.fileno())
            self.assertEqual(result_events, winpoll.POLLWRNORM)

    def test_pollin(self):
        obj = winpoll.wsapoll()

        with contextlib.ExitStack() as stack:
            sock1, sock2 = map(stack.enter_context, socket.socketpair())
            obj.register(sock2, winpoll.POLLIN)

            sock1.send(b"*")
            result = obj.poll()

            self.assertEqual(len(result), 1)

            result_fd, result_events = result[0]
            self.assertEqual(result_fd, sock2.fileno())
            self.assertEqual(result_events, winpoll.POLLRDNORM)

    def test_timeout(self):
        obj = winpoll.wsapoll()

        with contextlib.ExitStack() as stack:
            sock1, sock2 = map(stack.enter_context, socket.socketpair())
            obj.register(sock2, winpoll.POLLIN)
            obj.poll(0)  # ensure the pollfd buffer is up-to-date

            for timeout in range(5):
                timeout_ns = timeout * 1_000_000_000

                with self.subTest(timeout=timeout):
                    t0 = time.monotonic_ns()
                    result = obj.poll(timeout)
                    t1 = time.monotonic_ns()

                    self.assertEqual(len(result), 0)

                    dt = t1 - t0
                    self.assertGreaterEqual(dt, timeout_ns - UNDERSLEEP_TOLERANCE_NS)
                    self.assertLess(dt, timeout_ns + OVERSLEEP_TOLERANCE_NS)
