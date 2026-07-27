"""
Rule-based capability selector.

Default deterministic implementation of CapabilitySelector.

The selector interprets the reasoning result together with planning
insights and returns the capabilities required to execute the goal.

Future implementations may use semantic search, vector databases,
LLMs, reinforcement learning, or hybrid approaches without changing
the planner.
"""

from __future__ import annotations

from backend.core.agents.context import AgentContext
from backend.core.agents.goal import Goal
from backend.core.planning.capability_selector import (
    CapabilitySelector,
)
from backend.core.planning.planning_insights import (
    PlanningInsights,
)
from backend.core.planning.selected_capabilities import (
    SelectedCapabilities,
)
from backend.core.reasoning.reasoning_result import (
    ReasoningResult,
)


class RuleBasedCapabilitySelector(
    CapabilitySelector,
):
    """
    Default deterministic capability selector.
    """

    async def select(
        self,
        *,
        goal: Goal,
        context: AgentContext,
        reasoning: ReasoningResult,
        insights: PlanningInsights,
    ) -> SelectedCapabilities:
        """
        Select capabilities required for execution.
        """

        del goal
        del context

        capabilities: list[str] = []

        decision = (
            reasoning.decision.outcome.lower()
        )

        if decision == "execute":
            capabilities.append(
                "goal.execute",
            )
            capabilities.append(
                "goal.verify",
            )

        elif decision == "investigate":
            capabilities.extend(
                (
                    "memory.search",
                    "reasoning.analyze",
                    "goal.execute",
                )
            )

        elif decision == "clarify":
            capabilities.append(
                "user.ask",
            )

        else:
            capabilities.append(
                "goal.execute",
            )

        #
        # Prefer historically successful capabilities.
        #
        for capability in (
            insights.suggested_capabilities
        ):
            if capability not in capabilities:
                capabilities.append(
                    capability,
                )

        return SelectedCapabilities(
            capabilities=tuple(
                capabilities,
            ),
            metadata={
                "selector": (
                    self.__class__.__name__
                ),
                "reasoning_strategy": (
                    reasoning.strategy
                ),
                "reasoning_confidence": (
                    reasoning.confidence
                ),
                "history_available": (
                    insights.has_history
                ),
            },
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return selector diagnostics.
        """

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "type": "rule-based",
                "supported_decisions": (
                    "execute",
                    "investigate",
                    "clarify",
                ),
            }
        )

        return diagnostics