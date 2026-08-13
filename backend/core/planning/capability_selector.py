"""
Capability selector.

Defines the interface responsible for selecting the capabilities
required to accomplish a goal.

The selector evaluates:

- the goal
- the reasoning result
- planning insights

and returns the capabilities that should be used by the planning
policy.

Concrete implementations may use deterministic rules, semantic search,
vector similarity, machine learning, or LLM-based reasoning.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from backend.core.agents.context import AgentContext
from backend.core.agents.goal import Goal
from backend.core.planning.planning_insights import (
    PlanningInsights,
)
from backend.core.planning.selected_capabilities import (
    SelectedCapabilities,
)
from backend.core.reasoning.reasoning_result import (
    ReasoningResult,
)


class CapabilitySelector(ABC):
    """
    Base interface for capability selection.
    """

    @abstractmethod
    async def select(
        self,
        *,
        goal: Goal,
        context: AgentContext,
        reasoning: ReasoningResult,
        insights: PlanningInsights,
    ) -> SelectedCapabilities:
        """
        Select the capabilities required to execute the supplied goal.
        """

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return selector diagnostics.
        """

        return {
            "selector": self.__class__.__name__,
        }