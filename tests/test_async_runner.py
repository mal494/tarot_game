import asyncio
import threading
import time
import unittest

from ai.async_runner import AsyncRunnerCore


class AsyncRunnerCoreTests(unittest.TestCase):
    def setUp(self):
        self.callback_results = []
        self.core = AsyncRunnerCore(
            deliver_callback=lambda fn: fn(),
        )

    def tearDown(self):
        self.core.shutdown()

    def test_completes_multi_step_coroutine_on_background_loop(self):
        async def slow():
            await asyncio.sleep(0.05)
            return "done"

        self.core.run(slow(), callback=self.callback_results.append)
        time.sleep(0.2)

        self.assertEqual(self.callback_results, ["done"])

    def test_cancelled_coroutine_delivers_none(self):
        started = threading.Event()
        gate = asyncio.Event()

        async def wait_for_cancel():
            started.set()
            await gate.wait()
            return "should not finish"

        handle = self.core.run(wait_for_cancel(), callback=self.callback_results.append)
        self.assertTrue(started.wait(timeout=1.0))

        self.assertTrue(self.core.cancel(handle))
        time.sleep(0.2)

        self.assertEqual(self.callback_results, [None])

    def test_exception_delivers_none(self):
        async def fail():
            await asyncio.sleep(0.01)
            raise RuntimeError("boom")

        self.core.run(fail(), callback=self.callback_results.append)
        time.sleep(0.2)

        self.assertEqual(self.callback_results, [None])

    def test_blocking_work_does_not_require_main_thread_pump(self):
        async def needs_real_asyncio_sleep():
            await asyncio.sleep(0.08)
            return "ready"

        self.core.run(needs_real_asyncio_sleep(), callback=self.callback_results.append)
        time.sleep(0.2)

        self.assertEqual(self.callback_results, ["ready"])
