"""
Workflow result.

Represents the outcome of an executed workflow.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from backend.core.tasks.result import TaskResult


@dataclass(slots=True, frozen=True)
class WorkflowResult:
    """
    Result of workflow execution.
    """

    workflow: str

    success: bool

    task_results: tuple[TaskResult, ...] = ()

    started_at: datetime = field(
        default_factory=lambda: datetime.now(UTC),
    )

    finished_at: datetime | None = None

    metadata: dict[str, object] = field(
        default_factory=dict,
    )

    @property
    def task_count(self) -> int:
        """
        Number of executed tasks.
        """
        return len(self.task_results)

    @property
    def successful_tasks(self) -> int:
        """
        Number of successful tasks.
        """
        return sum(
            result.success
            for result in self.task_results
        )

    @property
    def failed_tasks(self) -> int:
        """
        Number of failed tasks.
        """
        return self.task_count - self.successful_tasks

    def diagnostics(self) -> dict[str, object]:
        """
        Return workflow diagnostics.
        """
        return {
            "workflow": self.workflow,
            "successful": self.success,
            "task_count": self.task_count,
            "successful_tasks": self.successful_tasks,
            "failed_tasks": self.failed_tasks,
            "started_at": self.started_at.isoformat(),
            "finished_at": (
                self.finished_at.isoformat()
                if self.finished_at is not None
                else None
            ),
            "metadata": self.metadata,
        }