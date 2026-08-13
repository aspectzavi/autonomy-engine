"""
Simple planner.

A minimal planner implementation that converts a goal into a single-step
execution plan.

This planner is intended for early development and testing. More
advanced planners (rule-based, LLM-driven, hybrid, etc.) can later
replace or extend this implementation without affecting the rest of the
architecture.
"""

from __future__ import annotations

from backend.core.agents.goal import Goal
from backend.core.planning.execution_plan import ExecutionPlan
from backend.core.planning.plan_step import PlanStep
from backend.core.planning.planner import Planner


class SimplePlanner(Planner):
    """
    Minimal planner implementation.
    """

    # ------------------------------------------------------------------
    # Planning
    # ------------------------------------------------------------------

    async def plan(
        self,
        goal: Goal,
    ) -> ExecutionPlan:
        """
        Produce a simple execution plan consisting of a single step.
        """

        step = PlanStep(
            id="step-1",
            name="Execute Goal",
            description=goal.description,
            capability="goal.execute",
        )

        return ExecutionPlan(
            name="Simple Execution Plan",
            description=goal.description,
            steps=(
                step,
            ),
            metadata={
                "planner": type(
                    self,
                ).__name__,
            },
        )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def supports(
        self,
        goal: Goal,
    ) -> bool:
        """
        This planner supports every goal.
        """

        return True

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Planner diagnostics.
        """

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "strategy": "simple",
                "multi_step": False,
            },
        )

        return diagnostics