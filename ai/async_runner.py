import asyncio
import threading
from concurrent.futures import Future
from typing import Any, Callable, Coroutine, Dict, Optional

try:
    # Ursina is required at runtime for the in‑game async runner, but the
    # test suite only relies on AsyncRunnerCore. Provide a lightweight
    # fallback so tests can run without the engine installed.
    from ursina import Entity, invoke  # type: ignore
except ImportError:  # pragma: no cover - exercised indirectly
    class Entity(object):  # type: ignore
        def __init__(self, *args, **kwargs) -> None:
            pass

    def invoke(fn: Callable[..., None], *args: Any, **kwargs: Any) -> None:  # type: ignore
        fn(*args, **kwargs)


Callback = Optional[Callable[[Any], None]]


class AsyncRunnerCore:
    """
    Runs coroutines on a dedicated background asyncio loop and delivers
    callbacks on the caller's thread via an injected delivery function.
    """

    def __init__(self, deliver_callback: Callable[[Callable[[], None]], None]):
        self._deliver = deliver_callback
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(
            target=self._run_loop,
            name="AsyncRunnerCore",
            daemon=True,
        )
        self._callbacks: Dict[Future, Callback] = {}
        self._task_boxes: Dict[Future, Dict[str, Optional[asyncio.Task]]] = {}
        self._thread.start()

    def _run_loop(self) -> None:
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def run(self, coro: Coroutine[Any, Any, Any], callback: Callback = None) -> Future:
        task_box: Dict[str, Optional[asyncio.Task]] = {"task": None}

        async def bridge() -> Any:
            task_box["task"] = asyncio.current_task()
            return await coro

        future = asyncio.run_coroutine_threadsafe(bridge(), self._loop)
        self._callbacks[future] = callback
        self._task_boxes[future] = task_box
        future.add_done_callback(self._on_future_done)
        return future

    def cancel(self, handle: Future) -> bool:
        if handle.done():
            return False

        if handle.cancel():
            return True

        task_box = self._task_boxes.get(handle)
        task = task_box.get("task") if task_box else None
        if task is None:
            return False

        def cancel_task() -> None:
            if not task.done():
                task.cancel()

        self._loop.call_soon_threadsafe(cancel_task)
        return True

    def shutdown(self) -> None:
        if self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join(timeout=1.0)
        if not self._loop.is_closed():
            self._loop.close()

    def _on_future_done(self, future: Future) -> None:
        callback = self._callbacks.pop(future, None)
        self._task_boxes.pop(future, None)
        if callback is None:
            return

        def deliver() -> None:
            if future.cancelled():
                callback(None)
                return
            try:
                callback(future.result())
            except Exception as exc:
                print("[AsyncRunner] Task error:", exc)
                callback(None)

        self._deliver(deliver)


class AsyncRunner(Entity):
    """
    Ursina-facing async runner. Coroutines execute off the main thread so the
    render loop never calls run_until_complete().
    """

    _instance = None

    @staticmethod
    def instance():
        if AsyncRunner._instance is None:
            AsyncRunner()
        return AsyncRunner._instance

    def __init__(self):
        if AsyncRunner._instance is not None:
            return

        super().__init__()
        AsyncRunner._instance = self

        def deliver(fn: Callable[[], None]) -> None:
            invoke(fn)

        self._core = AsyncRunnerCore(deliver_callback=deliver)

    def run(self, coro, callback=None):
        return self._core.run(coro, callback)

    def cancel(self, handle):
        return self._core.cancel(handle)

    def on_destroy(self):
        self._core.shutdown()
