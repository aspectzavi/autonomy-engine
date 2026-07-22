"""
Execution result.

Represents the final outcome of an autonomous runtime execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from backend.core.workflows.result import WorkflowResult


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    """
    Final runtime execution result.
    """

    success: bool

    workflow_result: WorkflowResult | None = None

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
            "workflow": (
                self.workflow_result.workflow
                if self.workflow_result is not None
                else None
            ),
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat(),
            "message": self.message,
            "errors": self.errors,
            "artifacts": self.artifacts,
            "metadata": self.metadata,
        }