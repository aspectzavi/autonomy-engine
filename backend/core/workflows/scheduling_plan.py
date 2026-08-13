"""
Scheduling plan.

Represents the ordered execution schedule for a workflow.

Each SchedulingGroup contains tasks that may execute concurrently.
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
class SchedulingPlan:
    """
    Immutable workflow schedule.
    """

    groups: tuple[SchedulingGroup, ...] = field(
        default_factory=tuple,
    )

    metadata: dict[str, object] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def group_count(
        self,
    ) -> int:
        return len(
            self.groups,
        )

    @property
    def node_count(
        self,
    ) -> int:
        return sum(
            group.size
            for group in self.groups
        )

    @property
    def is_empty(
        self,
    ) -> bool:
        return self.group_count == 0

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        return {
            "groups": self.group_count,
            "nodes": self.node_count,
            "metadata": self.metadata,
        }