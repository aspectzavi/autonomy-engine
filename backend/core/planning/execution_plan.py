"""
Execution plan.

Represents a validated execution plan produced by the planner.

The execution plan is an intermediate representation between a user
goal and an executable workflow.

The planner creates an ExecutionPlan.

The WorkflowBuilder later converts it into a Workflow.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from backend.core.planning.plan_step import PlanStep


@dataclass(frozen=True, slots=True)
class ExecutionPlan:
    """
    Immutable execution plan.
    """

    name: str

    description: str

    steps: tuple[PlanStep, ...]

    created_at: datetime = field(
        default_factory=lambda: datetime.now(
            UTC,
        ),
    )

    metadata: dict[str, object] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def step_count(
        self,
    ) -> int:
        """
        Number of plan steps.
        """

        return len(
            self.steps,
        )

    @property
    def is_empty(
        self,
    ) -> bool:
        """
        Whether the plan contains no steps.
        """

        return (
            self.step_count == 0
        )

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def step(
        self,
        step_id: str,
    ) -> PlanStep:
        """
        Retrieve a plan step.

        Raises:
            KeyError:
                If the step does not exist.
        """

        for step in self.steps:
            if step.id == step_id:
                return step

        raise KeyError(step_id)

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return execution plan diagnostics.
        """

        return {
            "name": self.name,
            "description": self.description,
            "step_count": self.step_count,
            "created_at": (
                self.created_at.isoformat()
            ),
            "steps": [
                step.diagnostics()
                for step in self.steps
            ],
            "metadata": self.metadata,
        }
