"""
Task executor.

Responsible for executing individual tasks.
"""

from __future__ import annotations

from backend.core.tasks.context import TaskContext
from backend.core.tasks.result import TaskResult
from backend.core.tasks.task import Task


class TaskExecutor:
    """
    Executes tasks.

    The executor owns execution only.
    Scheduling belongs to TaskScheduler.
    """

    async def execute(
        self,
        task: Task,
        context: TaskContext,
    ) -> TaskResult:
        """
        Execute a task.

        Returns:
            TaskResult:
                The task execution result.
        """
        return await task.execute(context)

    async def execute_many(
        self,
        tasks: list[Task],
        context: TaskContext,
    ) -> list[TaskResult]:
        """
        Execute multiple tasks sequentially.
        """
        results: list[TaskResult] = []

        for task in tasks:
            results.append(
                await self.execute(
                    task,
                    context,
                )
            )

        return results