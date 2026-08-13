"""
Abstract task definition.

Defines the base class for every executable task in the autonomy engine.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime

from backend.core.tasks.context import TaskContext
from backend.core.tasks.priority import TaskPriority
from backend.core.tasks.result import TaskResult
from backend.core.tasks.status import TaskStatus


class Task(ABC):
    """
    Base class for executable tasks.

    Public execution is owned by this class while subclasses
    implement the protected execution hook.
    """

    def __init__(
        self,
        *,
        name: str,
        priority: TaskPriority = TaskPriority.NORMAL,
    ) -> None:
        self._name = name
        self._priority = priority
        self._status = TaskStatus.CREATED

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        """
        Human-readable task name.
        """
        return self._name

    @property
    def priority(self) -> TaskPriority:
        """
        Task scheduling priority.
        """
        return self._priority

    @property
    def status(self) -> TaskStatus:
        """
        Current execution status.
        """
        return self._status

    @property
    def is_finished(self) -> bool:
        """
        Whether the task has reached a terminal state.
        """
        return self._status.is_terminal

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def execute(
        self,
        context: TaskContext,
    ) -> TaskResult:
        """
        Execute the task.
        """

        if context.is_cancelled:
            self._status = TaskStatus.CANCELLED

            return TaskResult.failure(
                "Execution cancelled.",
            )

        self._status = TaskStatus.RUNNING

        started = datetime.now(UTC)

        context.events.publish(
            "task.started",
            {
                "task": self.name,
            },
        )

        try:
            result = await self.run(context)

            self._status = TaskStatus.COMPLETED

            context.events.publish(
                "task.completed",
                {
                    "task": self.name,
                },
            )

            return TaskResult.ok(
                output=result,
                started_at=started,
            )

        except Exception as exc:
            self._status = TaskStatus.FAILED

            context.events.publish(
                "task.failed",
                {
                    "task": self.name,
                    "error": str(exc),
                },
            )

            return TaskResult.failure(
                str(exc),
                started_at=started,
            )

    # ------------------------------------------------------------------
    # Extension Hook
    # ------------------------------------------------------------------

    @abstractmethod
    async def run(
        self,
        context: TaskContext,
    ) -> object:
        """
        Execute task-specific logic.
        """

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(self) -> dict[str, object]:
        """
        Return task diagnostics.
        """
        return {
            "name": self.name,
            "priority": self.priority.name,
            "status": self.status.value,
        }