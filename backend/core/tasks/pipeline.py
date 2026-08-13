"""
Task pipeline.

Executes a sequence of tasks as a workflow.
"""

from __future__ import annotations

from backend.core.tasks.context import TaskContext
from backend.core.tasks.result import TaskResult
from backend.core.tasks.scheduler import TaskScheduler
from backend.core.tasks.task import Task


class TaskPipeline:
    """
    Sequential task pipeline.
    """

    def __init__(
        self,
        scheduler: TaskScheduler | None = None,
    ) -> None:
        self._scheduler = scheduler or TaskScheduler()

    @property
    def scheduler(self) -> TaskScheduler:
        """
        Pipeline scheduler.
        """
        return self._scheduler

    def add(
        self,
        task: Task,
    ) -> "TaskPipeline":
        """
        Add a task to the pipeline.

        Returns:
            TaskPipeline:
                The pipeline for fluent chaining.
        """
        self.scheduler.submit(task)
        return self

    async def run(
        self,
        context: TaskContext,
    ) -> list[TaskResult]:
        """
        Execute all queued tasks.
        """
        return await self.scheduler.run_all(context)

    def clear(self) -> None:
        """
        Remove all pending tasks.
        """
        self.scheduler.queue.clear()

    def diagnostics(self) -> dict[str, object]:
        """
        Return pipeline diagnostics.
        """
        return {
            "scheduler": self.scheduler.diagnostics(),
        }