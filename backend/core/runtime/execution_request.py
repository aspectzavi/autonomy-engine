"""
Execution request.

Represents a single autonomous execution request submitted to the
runtime coordinator.

The request is immutable and captures the information required to
plan and execute a user goal.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from backend.core.agents.goal import Goal


@dataclass(frozen=True, slots=True)
class ExecutionRequest:
    """
    Immutable runtime execution request.
    """

    goal: Goal

    request_id: str = field(
        default_factory=lambda: str(
            uuid4(),
        ),
    )

    created_at: datetime = field(
        default_factory=lambda: datetime.now(
            UTC,
        ),
    )

    priority: int = 0

    metadata: dict[str, object] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return request diagnostics.
        """
        return {
            "request_id": self.request_id,
            "goal": self.goal.description,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }