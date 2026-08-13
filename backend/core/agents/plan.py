"""
Agent plan.

Defines the result of high-level planning performed by an agent planner.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from backend.core.agents.goal import Goal


@dataclass(slots=True, frozen=True)
class Plan:
    """
    High-level execution plan for a goal.

    A plan captures the planning outcome before it is translated into an
    executable workflow.
    """

    goal: Goal

    description: str

    created_at: datetime = field(
        default_factory=lambda: datetime.now(UTC),
        kw_only=True,
    )

    @property
    def goal_description(self) -> str:
        """
        Return the goal description.
        """
        return self.goal.description

    def diagnostics(self) -> dict[str, object]:
        """
        Return plan diagnostics.
        """
        return {
            "goal": self.goal.description,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
        }