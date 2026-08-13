"""
Scheduling group.

Represents a group of workflow nodes that may execute in parallel.

A SchedulingGroup is produced by a WorkflowScheduler and consumed by
the workflow runtime.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


@dataclass(
    frozen=True,
    slots=True,
)
class SchedulingGroup:
    """
    Immutable execution group.
    """

    node_ids: tuple[str, ...] = field(
        default_factory=tuple,
    )

    metadata: dict[str, object] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def size(
        self,
    ) -> int:
        """
        Number of workflow nodes.
        """

        return len(
            self.node_ids,
        )

    @property
    def is_empty(
        self,
    ) -> bool:
        """
        Whether the group contains no nodes.
        """

        return self.size == 0

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return scheduling diagnostics.
        """

        return {
            "size": self.size,
            "nodes": self.node_ids,
            "metadata": self.metadata,
        }