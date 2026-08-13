"""
Workflow runtime report.

Represents the immutable report produced by a WorkflowRuntime.

A RuntimeReport summarizes the complete workflow lifecycle after
scheduling and execution have finished.

The report intentionally contains no mutable runtime state.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from backend.core.workflows.execution_result import (
    ExecutionResult,
)
from backend.core.workflows.scheduling_plan import (
    SchedulingPlan,
)


@dataclass(
    frozen=True,
    slots=True,
)
class RuntimeReport:
    """
    Immutable workflow runtime report.
    """

    schedule: SchedulingPlan

    execution: ExecutionResult

    metadata: dict[str, object] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def success(
        self,
    ) -> bool:
        """
        Whether workflow execution completed successfully.
        """

        return self.execution.success

    @property
    def completed_batches(
        self,
    ) -> int:
        """
        Number of completed scheduling groups.
        """

        return self.execution.completed_batches

    @property
    def completed_tasks(
        self,
    ) -> int:
        """
        Number of successfully completed tasks.
        """

        return self.execution.completed_tasks

    @property
    def failed_tasks(
        self,
    ) -> int:
        """
        Number of failed tasks.
        """

        return self.execution.failed_tasks

    @property
    def total_tasks(
        self,
    ) -> int:
        """
        Total executed tasks.
        """

        return self.execution.total_tasks

    @property
    def group_count(
        self,
    ) -> int:
        """
        Number of scheduling groups.
        """

        return self.schedule.group_count

    @property
    def has_failures(
        self,
    ) -> bool:
        """
        Whether execution encountered failures.
        """

        return self.execution.has_failures

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return runtime diagnostics.
        """

        return {
            "success": self.success,
            "groups": self.group_count,
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
            "schedule": (
                self.schedule.diagnostics()
            ),
            "execution": (
                self.execution.diagnostics()
            ),
            "metadata": (
                self.metadata
            ),
        }