"""
Planner.

Defines the interface for transforming a goal into an execution plan.

Concrete implementations may use rule-based planning, LLMs, hybrid
reasoning, or other planning strategies.

The planner itself is intentionally independent of workflow execution.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from backend.core.agents.goal import Goal
from backend.core.planning.execution_plan import ExecutionPlan


class Planner(ABC):
    """
    Abstract execution planner.
    """

    # ------------------------------------------------------------------
    # Planning
    # ------------------------------------------------------------------

    @abstractmethod
    async def plan(
        self,
        goal: Goal,
    ) -> ExecutionPlan:
        """
        Produce an execution plan for the supplied goal.

        Args:
            goal:
                Goal to plan.

        Returns:
            ExecutionPlan.

        Raises:
            PlanningError:
                If the goal cannot be planned.
        """

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @abstractmethod
    def supports(
        self,
        goal: Goal,
    ) -> bool:
        """
        Determine whether this planner can plan the supplied goal.
        """

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Planner diagnostics.
        """

        return {
            "planner": type(
                self,
            ).__name__,
        }