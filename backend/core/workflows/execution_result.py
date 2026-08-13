"""
Workflow execution result.

Represents the immutable outcome produced by a WorkflowExecutor.

ExecutionResult summarizes the execution of an entire scheduling plan.

It intentionally contains no mutable runtime state.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


@dataclass(
    frozen=True,
    slots=True,
)
class ExecutionResult:
    """
    Immutable workflow execution result.
    """

    success: bool

    completed_batches: int = 0

    completed_tasks: int = 0

    failed_tasks: int = 0

    metadata: dict[str, object] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def has_failures(
        self,
    ) -> bool:
        """
        Whether execution contained failures.
        """

        return self.failed_tasks > 0

    @property
    def total_tasks(
        self,
    ) -> int:
        """
        Total executed tasks.
        """

        return (
            self.completed_tasks
            + self.failed_tasks
        )

    @property
    def is_empty(
        self,
    ) -> bool:
        """
        Whether nothing executed.
        """

        return (
            self.completed_batches == 0
            and self.total_tasks == 0
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return execution diagnostics.
        """

        return {
            "success": self.success,
            "completed_batches": (
                self.completed_batches
            ),
            "completed_tasks": (
                self.completed_tasks
            ),
            "failed_tasks": (
                self.failed_tasks
            ),
            "total_tasks": (
                self.total_tasks
            ),
            "metadata": (
                self.metadata
            ),
        }