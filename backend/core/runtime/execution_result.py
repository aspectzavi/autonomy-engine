"""
Execution result.

Represents the final outcome of an autonomous runtime execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from datetime import UTC
from datetime import datetime

from backend.core.workflows.runtime_report import (
    RuntimeReport,
)


@dataclass(
    frozen=True,
    slots=True,
)
class ExecutionResult:
    """
    Final runtime execution result.
    """

    success: bool

    workflow_result: RuntimeReport | None = None

    started_at: datetime = field(
        default_factory=lambda: datetime.now(
            UTC,
        ),
    )

    finished_at: datetime = field(
        default_factory=lambda: datetime.now(
            UTC,
        ),
    )

    message: str = ""

    errors: tuple[str, ...] = ()

    artifacts: dict[str, object] = field(
        default_factory=dict,
    )

    metadata: dict[str, object] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def duration_seconds(
        self,
    ) -> float:
        """
        Total runtime duration.
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
        Return execution result diagnostics.
        """

        return {
            "success": self.success,
            "workflow_success": (
                self.workflow_result.success
                if self.workflow_result is not None
                else None
            ),
            "started_at": (
                self.started_at.isoformat()
            ),
            "finished_at": (
                self.finished_at.isoformat()
            ),
            "duration_seconds": (
                self.duration_seconds
            ),
            "message": self.message,
            "errors": self.errors,
            "artifacts": self.artifacts,
            "metadata": self.metadata,
        } 