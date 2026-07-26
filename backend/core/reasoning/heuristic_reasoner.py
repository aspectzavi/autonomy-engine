"""
Heuristic reasoner.

Provides the default reasoning strategy for the autonomy engine.

This implementation intentionally uses deterministic heuristics rather
than an LLM. It forms the baseline reasoning capability and guarantees
that the engine can operate without external AI services.

Future implementations may replace or augment this strategy with
LLM-backed reasoning.
"""

from __future__ import annotations

from backend.core.reasoning.reasoning_context import (
    ReasoningContext,
)
from backend.core.reasoning.reasoning_request import (
    ReasoningRequest,
)
from backend.core.reasoning.reasoning_result import (
    ReasoningResult,
)
from backend.core.reasoning.strategy import (
    Strategy,
)


class HeuristicReasoner(Strategy):
    """
    Default heuristic reasoning strategy.
    """

    # ------------------------------------------------------------------
    # Reasoning
    # ------------------------------------------------------------------

    async def reason(
        self,
        request: ReasoningRequest,
        context: ReasoningContext,
    ) -> ReasoningResult:
        """
        Produce a reasoning result using simple heuristics.

        This implementation intentionally performs no AI reasoning.
        It establishes the architecture upon which future reasoning
        strategies will build.
        """

        strategy = "default"

        rationale = (
            "Selected the default reasoning strategy "
            "using deterministic heuristics."
        )

        if request.has_constraints:
            rationale += (
                " Execution constraints were provided."
            )

        if request.has_context:
            rationale += (
                " Runtime context was provided."
            )

        context.events.publish(
            "reasoning.completed",
            {
                "goal": request.goal,
                "strategy": strategy,
            },
        )

        return ReasoningResult(
            strategy=strategy,
            confidence=1.0,
            rationale=rationale,
            metadata={
                "reasoner": self.__class__.__name__,
            },
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return diagnostics.
        """

        return {
            "strategy": "heuristic",
            "llm": False,
        }