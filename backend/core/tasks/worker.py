"""
Task worker.

Continuously executes scheduled tasks.
"""

from __future__ import annotations

import asyncio

from backend.core.tasks.context import TaskContext
from backend.core.tasks.scheduler import TaskScheduler


class TaskWorker:
    """
    Background task worker.

    Continuously executes queued tasks until stopped.
    """

    def __init__(
        self,
        scheduler: TaskScheduler,
    ) -> None:
        self._scheduler = scheduler
        self._running = False

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def scheduler(self) -> TaskScheduler:
        """
        Associated task scheduler.
        """
        return self._scheduler

    @property
    def is_running(self) -> bool:
        """
        Whether the worker is currently running.
        """
        return self._running

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(
        self,
        context: TaskContext,
        *,
        poll_interval: float = 0.1,
    ) -> None:
        """
        Start processing queued tasks.

        The worker continues until stop() is called.
        """
        self._running = True

        while self._running:
            if self.scheduler.queue.empty:
                await asyncio.sleep(poll_interval)
                continue

            await self.scheduler.run_next(context)

    def stop(self) -> None:
        """
        Stop the worker.
        """
        self._running = False

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(self) -> dict[str, object]:
        """
        Return worker diagnostics.
        """
        return {
            "running": self.is_running,
            "scheduler": self.scheduler.diagnostics(),
        }