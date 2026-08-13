"""
Recovery report.

Represents the immutable outcome of a workflow recovery attempt.

RecoveryReport summarizes whether a workflow was successfully restored
from a checkpoint together with the recovered execution state.

Future versions may additionally include:

- recovery duration
- replay statistics
- migration information
- recovery warnings
- checkpoint versioning
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


@dataclass(
    frozen=True,
    slots=True,
)
class RecoveryReport:
    """
    Immutable workflow recovery report.
    """

    recovered: bool

    workflow: str

    checkpoint_found: bool

    checkpoint_id: str | None = None

    completed_nodes: int = 0

    pending_nodes: int = 0

    failed_nodes: int = 0

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
        Total workflow nodes represented by the checkpoint.
        """

        return (
            self.completed_nodes
            + self.pending_nodes
            + self.failed_nodes
        )

    @property
    def completion_ratio(
        self,
    ) -> float:
        """
        Completion ratio represented by the checkpoint.
        """

        if self.total_nodes == 0:
            return 1.0

        return (
            self.completed_nodes
            / self.total_nodes
        )

    @property
    def is_complete(
        self,
    ) -> bool:
        """
        Whether the recovered workflow was already complete.
        """

        return self.pending_nodes == 0

    @property
    def has_failures(
        self,
    ) -> bool:
        """
        Whether failed nodes were recovered.
        """

        return self.failed_nodes > 0

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return recovery diagnostics.
        """

        return {
            "recovered": self.recovered,
            "workflow": self.workflow,
            "checkpoint_found": (
                self.checkpoint_found
            ),
            "checkpoint_id": (
                self.checkpoint_id
            ),
            "completed_nodes": (
                self.completed_nodes
            ),
            "pending_nodes": (
                self.pending_nodes
            ),
            "failed_nodes": (
                self.failed_nodes
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