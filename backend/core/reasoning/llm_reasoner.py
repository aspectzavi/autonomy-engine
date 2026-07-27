"""
LLM reasoner.

Provides the architecture for LLM-backed reasoning.

This implementation intentionally does not communicate with an external
LLM provider yet. Instead, it establishes the interface and data flow
that future integrations (OpenAI, Anthropic, Gemini, local models, etc.)
will use.

Future implementations will:

- build prompts
- invoke an LLM
- parse structured responses
- generate reasoning traces
- produce confidence scores
"""

from __future__ import annotations

from datetime import UTC
from datetime import datetime

from backend.core.reasoning.decision import Decision
from backend.core.reasoning.decision_score import (
    DecisionScorer,
)
from backend.core.reasoning.prompt_builder import (
    PromptBuilder,
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


class LLMReasoner(Reasoner):
    """
    Placeholder implementation for future LLM reasoning.
    """

    def __init__(
        self,
        *,
        prompt_builder: PromptBuilder | None = None,
    ) -> None:
        self._prompt_builder = (
            prompt_builder
            or PromptBuilder()
        )

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

        return "llm"

    @property
    def prompt_builder(
        self,
    ) -> PromptBuilder:
        """
        Prompt builder.
        """

        return self._prompt_builder

    # ------------------------------------------------------------------
    # Reasoning
    # ------------------------------------------------------------------

    async def reason(
        self,
        request: ReasoningRequest,
        context: ReasoningContext,
    ) -> ReasoningResult:
        """
        Execute LLM reasoning.

        Currently this implementation builds the prompt and returns a
        placeholder decision until an LLM provider is integrated.
        """

        prompt = self.prompt_builder.build(
            request,
            context,
        )

        trace = ReasoningTrace()

        trace.add_step(
            ReasoningStep(
                name="Build prompt",
                description=(
                    "Constructed prompt for LLM reasoning."
                ),
                operation="prompt.build",
                success=True,
                confidence=1.0,
                observations=(
                    "Prompt successfully generated.",
                ),
                started_at=datetime.now(
                    UTC,
                ),
                finished_at=datetime.now(
                    UTC,
                ),
            )
        )

        trace.add_step(
            ReasoningStep(
                name="LLM invocation",
                description=(
                    "LLM provider not configured."
                ),
                operation="llm.invoke",
                success=True,
                confidence=0.5,
                observations=(
                    "Placeholder implementation.",
                ),
                started_at=datetime.now(
                    UTC,
                ),
                finished_at=datetime.now(
                    UTC,
                ),
            )
        )

        score = self._scorer.score(
            evidence_score=0.50,
            strategy_score=1.00,
            memory_score=0.75,
        )

        decision = Decision(
            name="LLM placeholder decision",
            description=(
                "LLM reasoning is not yet connected to a "
                "provider. Returning placeholder decision."
            ),
            outcome="proceed",
            confidence=score.confidence,
            evidence=(
                "Prompt successfully generated.",
                "No LLM provider configured.",
            ),
            recommendations=(
                "Integrate an LLM provider.",
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
            rationale=(
                "Prompt generated successfully. "
                "Placeholder response returned because "
                "no LLM provider has been configured."
            ),
            metadata={
                "reasoner": type(self).__name__,
                "prompt_length": len(prompt),
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
            "provider": None,
            "prompt_builder": type(
                self.prompt_builder,
            ).__name__,
            "llm_enabled": False,
        }