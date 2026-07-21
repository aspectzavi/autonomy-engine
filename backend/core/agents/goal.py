"""
Agent goal.

Defines the high-level objective assigned to an autonomous agent.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


@dataclass(slots=True, frozen=True)
class Goal:
    """
    High-level objective for an autonomous agent.

    A goal is translated into an executable workflow by an
    AgentPlanner.
    """

    description: str

    id: str = field(
        default_factory=lambda: str(uuid4()),
    )

    priority: int = 0

    constraints: tuple[str, ...] = ()

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    created_at: datetime = field(
        default_factory=lambda: datetime.now(UTC),
    )

    @property
    def has_constraints(self) -> bool:
        """
        Whether the goal defines execution constraints.
        """
        return bool(self.constraints)

    def with_metadata(
        self,
        **metadata: Any,
    ) -> "Goal":
        """
        Return a new goal with additional metadata.
        """
        updated = dict(self.metadata)
        updated.update(metadata)

        return Goal(
            id=self.id,
            description=self.description,
            priority=self.priority,
            constraints=self.constraints,
            metadata=updated,
            created_at=self.created_at,
        )

    def diagnostics(self) -> dict[str, object]:
        """
        Return goal diagnostics.
        """
        return {
            "id": self.id,
            "description": self.description,
            "priority": self.priority,
            "constraints": list(self.constraints),
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }