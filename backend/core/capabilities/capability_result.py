"""
Capability result.

Represents the outcome of executing a capability.

Capability results are returned by capability providers and later become
inputs to tasks, workflows, planners, and memory.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class CapabilityResult:
    """
    Result produced by a capability execution.
    """

    success: bool

    output: Any = None

    error: str | None = None

    metadata: dict[str, object] = field(
        default_factory=dict,
    )

    started_at: datetime = field(
        default_factory=lambda: datetime.now(UTC),
    )

    finished_at: datetime = field(
        default_factory=lambda: datetime.now(UTC),
    )

    # ------------------------------------------------------------------
    # Constructors
    # ------------------------------------------------------------------

    @classmethod
    def ok(
        cls,
        *,
        output: Any = None,
        metadata: dict[str, object] | None = None,
    ) -> CapabilityResult:
        """
        Successful execution.
        """

        now = datetime.now(UTC)

        return cls(
            success=True,
            output=output,
            metadata=metadata or {},
            started_at=now,
            finished_at=now,
        )

    @classmethod
    def failure(
        cls,
        error: str,
        *,
        metadata: dict[str, object] | None = None,
    ) -> CapabilityResult:
        """
        Failed execution.
        """

        now = datetime.now(UTC)

        return cls(
            success=False,
            error=error,
            metadata=metadata or {},
            started_at=now,
            finished_at=now,
        )

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    @property
    def failed(
        self,
    ) -> bool:
        """
        Whether execution failed.
        """

        return not self.success

    @property
    def duration_seconds(
        self,
    ) -> float:
        """
        Execution duration.
        """

        return (
            self.finished_at
            - self.started_at
        ).total_seconds()

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Capability result diagnostics.
        """

        return {
            "success": self.success,
            "failed": self.failed,
            "error": self.error,
            "duration_seconds": self.duration_seconds,
            "metadata": self.metadata,
        }