"""
Task scheduler.

Coordinates task execution using a queue and executor.
"""

from __future__ import annotations

from backend.core.tasks.context import TaskContext
from backend.core.tasks.executor import TaskExecutor
from backend.core.tasks.queue import TaskQueue
from backend.core.tasks.result import TaskResult
from backend.core.tasks.task import Task


class TaskScheduler:
    """
    Coordinates queued task execution.
    """

    def __init__(
        self,
        queue: TaskQueue | None = None,
        executor: TaskExecutor | None = None,
    ) -> None:
        self._queue = queue or TaskQueue()
        self._executor = executor or TaskExecutor()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def queue(self) -> TaskQueue:
        """
        Task queue.
        """
        return self._queue

    @property
    def executor(self) -> TaskExecutor:
        """
        Task executor.
        """
        return self._executor

    # ------------------------------------------------------------------
    # Scheduling
    # ------------------------------------------------------------------

    def submit(
        self,
        task: Task,
    ) -> None:
        """
        Submit a task for execution.
        """
        self.queue.enqueue(task)

    async def run_next(
        self,
        context: TaskContext,
    ) -> TaskResult:
        """
        Execute the next queued task.

        Raises:
            IndexError:
                If the queue is empty.
        """
        task = self.queue.dequeue()

        return await self.executor.execute(
            task,
            context,
        )

    async def run_all(
        self,
        context: TaskContext,
    ) -> list[TaskResult]:
        """
        Execute every queued task.
        """
        results: list[TaskResult] = []

        while not self.queue.empty:
            results.append(
                await self.run_next(context)
            )

        return results

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(self) -> dict[str, object]:
        """
        Return scheduler diagnostics.
        """
        return {
            "queue": self.queue.diagnostics(),
            "executor": self.executor.__class__.__name__,
        }