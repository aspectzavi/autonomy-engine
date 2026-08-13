"""
Heuristic reasoner.

Provides the default deterministic reasoning strategy.

This implementation intentionally performs no LLM reasoning. Instead it
constructs a complete reasoning trace using simple deterministic
heuristics.

Future LLM-based and hybrid reasoners should follow the same structure.
"""

from __future__ import annotations

from datetime import UTC
from datetime import datetime

from backend.core.reasoning.decision import Decision
from backend.core.reasoning.decision_score import (
    DecisionScorer,
)
from backend.core.reasoning.reasoner import (
    Reasoner,
)
from backend.core.reasoning.reasoning_context import (
    ReasoningContext,
)
from backend.core.reasoning.reasoning_request import (
    ReasoningRequest,
)
from backend.core.reasoning.reasoning_result import (
    ReasoningResult,
)
from backend.core.reasoning.reasoning_step import (
    ReasoningStep,
)
from backend.core.reasoning.reasoning_trace import (
    ReasoningTrace,
)


class HeuristicReasoner(Reasoner):
    """
    Default deterministic reasoning strategy.
    """

    def __init__(
        self,
    ) -> None:
        self._scorer = DecisionScorer()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def name(
        self,
    ) -> str:
        """
        Strategy name.
        """

        return "heuristic"

    # ------------------------------------------------------------------
    # Reasoning
    # ------------------------------------------------------------------

    async def reason(
        self,
        request: ReasoningRequest,
        context: ReasoningContext,
    ) -> ReasoningResult:
        """
        Produce a deterministic reasoning result.
        """

        trace = ReasoningTrace()

        #
        # Step 1
        #
        step = ReasoningStep(
            name="Analyze request",
            description=(
                "Analyze the incoming reasoning request."
            ),
            operation="request.analysis",
            success=True,
            confidence=1.0,
            observations=(
                "Goal received.",
            ),
            started_at=datetime.now(
                UTC,
            ),
            finished_at=datetime.now(
                UTC,
            ),
        )

        trace.add_step(
            step,
        )

        rationale = (
            "Selected the heuristic reasoning strategy."
        )

        if request.has_constraints:
            rationale += (
                " Constraints were considered."
            )

        if request.has_context:
            rationale += (
                " Runtime context was available."
            )

        score = self._scorer.score(
            evidence_score=1.0,
            strategy_score=1.0,
            memory_score=0.75,
        )

        decision = Decision(
            name="Default heuristic decision",
            description=rationale,
            outcome="proceed",
            confidence=score.confidence,
            evidence=(
                "Deterministic heuristic strategy selected.",
            ),
            recommendations=(
                "Proceed with planning.",
            ),
            metadata={
                "reasoner": self.name,
            },
        )

        trace.finish()

        context.events.publish(
            "reasoning.completed",
            {
                "goal": request.goal,
                "strategy": self.name,
                "confidence": score.confidence,
            },
        )

        return ReasoningResult(
            strategy=self.name,
            decision=decision,
            trace=trace,
            confidence=score.confidence,
            rationale=rationale,
            metadata={
                "reasoner": type(self).__name__,
                "score": score.diagnostics(),
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
            "strategy": self.name,
            "llm": False,
            "scorer": type(
                self._scorer,
            ).__name__,
        }