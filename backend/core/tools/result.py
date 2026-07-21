"""
Tool execution result.

Defines the standardized result returned by every executable tool.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(slots=True, frozen=True)
class ToolResult:
    """
    Result of a completed tool execution.
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
        Whether tool execution failed.
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
    ) -> "ToolResult":
        """
        Create a successful tool result.
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
    ) -> "ToolResult":
        """
        Create a failed tool result.
        """
        return cls(
            success=False,
            error=error,
            started_at=started_at,
            metadata=metadata or {},
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return result diagnostics.
        """
        return {
            "success": self.success,
            "failed": self.failed,
            "duration_seconds": self.duration_seconds,
            "metadata": self.metadata,
        }