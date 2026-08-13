"""
Workflow checkpoint.

Represents an immutable snapshot of workflow execution that can be
persisted and later restored.

WorkflowCheckpoint intentionally captures only durable execution state.
Runtime-specific resources (threads, sockets, processes, etc.) are not
included.

Future implementations may additionally support:

- incremental checkpoints
- compressed checkpoints
- encrypted checkpoints
- distributed persistence
- version migration
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from datetime import UTC
from datetime import datetime


@dataclass(
    frozen=True,
    slots=True,
)
class WorkflowCheckpoint:
    """
    Immutable workflow checkpoint.
    """

    workflow: str

    checkpoint_id: str

    created_at: datetime = field(
        default_factory=lambda: datetime.now(
            UTC,
        ),
    )

    completed_nodes: tuple[str, ...] = ()

    pending_nodes: tuple[str, ...] = ()

    failed_nodes: tuple[str, ...] = ()

    metadata: dict[str, object] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def total_nodes(
        self,
    ) -> int:
        """
        Total number of workflow nodes.
        """

        return (
            len(self.completed_nodes)
            + len(self.pending_nodes)
            + len(self.failed_nodes)
        )

    @property
    def completed_count(
        self,
    ) -> int:
        """
        Number of completed nodes.
        """

        return len(
            self.completed_nodes,
        )

    @property
    def pending_count(
        self,
    ) -> int:
        """
        Number of pending nodes.
        """

        return len(
            self.pending_nodes,
        )

    @property
    def failed_count(
        self,
    ) -> int:
        """
        Number of failed nodes.
        """

        return len(
            self.failed_nodes,
        )

    @property
    def completion_ratio(
        self,
    ) -> float:
        """
        Completion ratio.

        Returns a value between 0.0 and 1.0.
        """

        if self.total_nodes == 0:
            return 1.0

        return (
            self.completed_count
            / self.total_nodes
        )

    @property
    def is_complete(
        self,
    ) -> bool:
        """
        Whether the workflow has completed.
        """

        return (
            self.pending_count == 0
        )

    @property
    def has_failures(
        self,
    ) -> bool:
        """
        Whether any workflow node failed.
        """

        return self.failed_count > 0

    @property
    def is_empty(
        self,
    ) -> bool:
        """
        Whether the checkpoint contains no nodes.
        """

        return self.total_nodes == 0

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return checkpoint diagnostics.
        """

        return {
            "workflow": self.workflow,
            "checkpoint_id": self.checkpoint_id,
            "created_at": (
                self.created_at.isoformat()
            ),
            "completed_nodes": (
                self.completed_count
            ),
            "pending_nodes": (
                self.pending_count
            ),
            "failed_nodes": (
                self.failed_count
            ),
            "total_nodes": (
                self.total_nodes
            ),
            "completion_ratio": (
                self.completion_ratio
            ),
            "is_complete": (
                self.is_complete
            ),
            "has_failures": (
                self.has_failures
            ),
            "metadata": (
                self.metadata
            ),
        }