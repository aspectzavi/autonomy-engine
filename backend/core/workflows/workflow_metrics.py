"""
Workflow metrics.

Represents immutable execution metrics collected during workflow
execution.

WorkflowMetrics intentionally contains only summarized information.

Future versions may additionally include:

- CPU utilization
- memory usage
- I/O statistics
- network statistics
- latency histograms
- resource utilization
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


@dataclass(
    frozen=True,
    slots=True,
)
class WorkflowMetrics:
    """
    Immutable workflow metrics.
    """

    workflow: str = ""

    successful: bool = False

    completed_batches: int = 0

    completed_tasks: int = 0

    failed_tasks: int = 0

    metadata: dict[str, object] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Derived Metrics
    # ------------------------------------------------------------------

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
    def success_rate(
        self,
    ) -> float:
        """
        Task success rate.
        """

        total = self.total_tasks

        if total == 0:
            return 1.0

        return self.completed_tasks / total

    @property
    def failure_rate(
        self,
    ) -> float:
        """
        Task failure rate.
        """

        return 1.0 - self.success_rate

    @property
    def has_failures(
        self,
    ) -> bool:
        """
        Whether any task failed.
        """

        return self.failed_tasks > 0

    @property
    def is_empty(
        self,
    ) -> bool:
        """
        Whether no execution occurred.
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
        Return workflow metrics diagnostics.
        """

        return {
            "workflow": self.workflow,
            "successful": self.successful,
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
            "success_rate": (
                self.success_rate
            ),
            "failure_rate": (
                self.failure_rate
            ),
            "metadata": (
                self.metadata
            ),
        }