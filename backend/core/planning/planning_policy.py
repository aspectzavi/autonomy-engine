"""
Planning policy.

Defines the interface responsible for translating a reasoning outcome
into an execution plan.

A PlanningPolicy separates planning behaviour from the planner itself.

Responsibilities:

- interpret the ReasoningResult
- determine planning strategy
- produce an ExecutionPlan

This allows multiple planning implementations (rule-based, LLM-driven,
adaptive, etc.) without modifying the planner.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from backend.core.agents.context import AgentContext
from backend.core.agents.goal import Goal
from backend.core.planning.execution_plan import (
    ExecutionPlan,
)
from backend.core.planning.planning_insights import (
    PlanningInsights,
)
from backend.core.reasoning.reasoning_result import (
    ReasoningResult,
)


class PlanningPolicy(ABC):
    """
    Base interface for planning policies.

    A planning policy converts a reasoning result into an executable
    execution plan.
    """

    @abstractmethod
    async def build_plan(
        self,
        *,
        goal: Goal,
        context: AgentContext,
        reasoning: ReasoningResult,
        insights: PlanningInsights,
    ) -> ExecutionPlan:
        """
        Build an execution plan.

        Args:
            goal:
                Goal supplied by the runtime.

            context:
                Runtime execution context.

            reasoning:
                Result produced by the reasoning subsystem.

            insights:
                Planning insights produced by the memory analyzer.

        Returns:
            A fully constructed execution plan.
        """

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return policy diagnostics.
        """

        return {
            "policy": self.__class__.__name__,
        }