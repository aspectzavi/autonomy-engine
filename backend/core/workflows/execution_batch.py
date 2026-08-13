"""
Execution batch.

Represents one executable scheduling group.

An ExecutionBatch is produced by the WorkflowExecutor from a
SchedulingGroup.

Initially batches execute sequentially.

Future implementations may execute all tasks inside a batch
concurrently.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from backend.core.workflows.scheduling_group import (
    SchedulingGroup,
)


@dataclass(
    frozen=True,
    slots=True,
)
class ExecutionBatch:
    """
    Immutable execution batch.
    """

    group: SchedulingGroup

    order: int

    metadata: dict[str, object] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def task_ids(
        self,
    ) -> tuple[str, ...]:
        """
        Task identifiers contained in this batch.
        """

        return self.group.node_ids

    @property
    def task_count(
        self,
    ) -> int:
        """
        Number of tasks.
        """

        return self.group.size

    @property
    def is_parallel(
        self,
    ) -> bool:
        """
        Whether the batch contains multiple executable tasks.
        """

        return self.task_count > 1

    @property
    def is_empty(
        self,
    ) -> bool:
        """
        Whether the batch contains no tasks.
        """

        return self.group.is_empty

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return batch diagnostics.
        """

        return {
            "order": self.order,
            "task_count": self.task_count,
            "parallel": self.is_parallel,
            "task_ids": self.task_ids,
            "metadata": self.metadata,
        }