"""
Task execution result.

Defines the standardized result returned by every executable task.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(slots=True, frozen=True)
class TaskResult:
    """
    Result of a completed task execution.
    """

    success: bool

    output: Any = None

    error: str | None = None

    started_at: datetime | None = None

    finished_at: datetime = field(
        default_factory=lambda: datetime.now(UTC),
    )

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    @property
    def failed(self) -> bool:
        """
        Whether execution failed.
        """
        return not self.success

    @property
    def duration_seconds(self) -> float | None:
        """
        Execution duration in seconds.

        Returns None if the start time is unavailable.
        """
        if self.started_at is None:
            return None

        return (
            self.finished_at - self.started_at
        ).total_seconds()

    @classmethod
    def ok(
        cls,
        output: Any = None,
        *,
        started_at: datetime | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "TaskResult":
        """
        Create a successful task result.
        """
        return cls(
            success=True,
            output=output,
            started_at=started_at,
            metadata=metadata or {},
        )

    @classmethod
    def failure(
        cls,
        error: str,
        *,
        started_at: datetime | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "TaskResult":
        """
        Create a failed task result.
        """
        return cls(
            success=False,
            error=error,
            started_at=started_at,
            metadata=metadata or {},
        )