"""
Registry-aware capability selector.

Extends the deterministic decision-based selection (execute /
investigate / clarify) with keyword matching against the actual
registered capabilities (real tools -- browser_navigate,
desktop_click_element, browser_scrape, ...), so a goal whose
description overlaps a real capability's name or description gets
routed to that real capability instead of always falling through to
the abstract "goal.execute" placeholder.

This is deliberately simple keyword overlap, not NLU or an LLM call --
consistent with every other "RuleBased" component in this codebase,
and with the project's stated goal of deterministic, low-token-cost
execution wherever possible. It is a starting point: a goal has to
share actual words with a capability's name/description to be routed
correctly. Falls back to the exact behavior of
RuleBasedCapabilitySelector (the abstract placeholder set) whenever no
registry is supplied or nothing matches well enough, so this is a
strict superset of the previous behavior, never a regression.
"""

from __future__ import annotations

import re

from backend.core.agents.context import AgentContext
from backend.core.agents.goal import Goal
from backend.core.capabilities.capability_registry import (
    CapabilityRegistry,
)
from backend.core.planning.planning_insights import (
    PlanningInsights,
)
from backend.core.planning.rule_based_capability_selector import (
    RuleBasedCapabilitySelector,
)
from backend.core.planning.selected_capabilities import (
    SelectedCapabilities,
)
from backend.core.reasoning.reasoning_result import (
    ReasoningResult,
)

_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")

#
# A word needs at least this many shared tokens with a capability's
# name+description to be considered a real match, not just an
# incidental overlap on a common word like "the" or "get".
#
_MINIMUM_SHARED_TOKENS = 2


def _tokens(text: str) -> set[str]:
    return set(_TOKEN_PATTERN.findall(text.casefold()))


class RegistryAwareCapabilitySelector(
    RuleBasedCapabilitySelector,
):
    """
    Capability selector that prefers real registered capabilities
    over the abstract placeholder set when the goal's wording
    matches one well enough.
    """

    def __init__(
        self,
        *,
        capability_registry: CapabilityRegistry | None = None,
    ) -> None:
        self._capability_registry = capability_registry

    # ------------------------------------------------------------------
    # Selection
    # ------------------------------------------------------------------

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

        base = await super().select(
            goal=goal,
            context=context,
            reasoning=reasoning,
            insights=insights,
        )

        match = self._best_match(goal)

        if match is None:
            return base

        #
        # Replace the abstract "goal.execute" placeholder with the
        # real matched capability -- keep everything else (goal.
        # verify, memory.search, ...) the decision selected.
        #
        capabilities = tuple(
            match if capability == "goal.execute" else capability
            for capability in base.capabilities
        )

        metadata = dict(base.metadata)
        metadata["matched_capability"] = match

        return SelectedCapabilities(
            capabilities=capabilities,
            metadata=metadata,
        )

    # ------------------------------------------------------------------
    # Matching
    # ------------------------------------------------------------------

    def _best_match(
        self,
        goal: Goal,
    ) -> str | None:
        if self._capability_registry is None:
            return None

        goal_tokens = _tokens(goal.description)

        if not goal_tokens:
            return None

        best_name: str | None = None
        best_score = 0

        for capability in (
            self._capability_registry.capabilities
        ):
            candidate_tokens = _tokens(
                f"{capability.name} {capability.description}",
            )

            score = len(
                goal_tokens & candidate_tokens,
            )

            if score > best_score:
                best_score = score
                best_name = capability.name

        if best_score < _MINIMUM_SHARED_TOKENS:
            return None

        return best_name
