"""
Reasoning pipeline.

Coordinates the complete reasoning workflow for the autonomy engine.

The pipeline is responsible for:

- building a ReasoningRequest
- creating a ReasoningContext
- invoking the ReasoningEngine
- returning the resulting ReasoningResult

It intentionally performs no planning. Its sole responsibility is
orchestrating the reasoning subsystem.
"""

from __future__ import annotations

from backend.core.agents.context import AgentContext
from backend.core.agents.goal import Goal
from backend.core.memory.memory import Memory
from backend.core.reasoning.reasoning_context import (
    ReasoningContext,
)
from backend.core.reasoning.reasoning_engine import (
    ReasoningEngine,
)
from backend.core.reasoning.reasoning_request import (
    ReasoningRequest,
)
from backend.core.reasoning.reasoning_result import (
    ReasoningResult,
)


class ReasoningPipeline:
    """
    Coordinates execution of the reasoning subsystem.
    """

    def __init__(
        self,
        *,
        engine: ReasoningEngine,
    ) -> None:
        self._engine = engine

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def engine(
        self,
    ) -> ReasoningEngine:
        """
        Underlying reasoning engine.
        """

        return self._engine

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def run(
        self,
        *,
        goal: Goal,
        context: AgentContext,
    ) -> ReasoningResult:
        """
        Execute the complete reasoning pipeline.
        """

        request = ReasoningRequest(
            goal=goal.description,
            context={
                "goal_description": goal.description,
            },
            constraints={},
            metadata={
                "goal_id": goal.id,
            },
        )

        reasoning_context = ReasoningContext(
            memory=self._memory(context),
            events=context.event_bus,
        )

        return await self.engine.reason(
            request,
            reasoning_context,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _memory(
        self,
        context: AgentContext,
    ) -> Memory:
        """
        Resolve a Memory instance for reasoning.

        Reasoning currently requires a Memory implementation even when
        no runtime memory service has been attached.
        """

        if (
            context.runtime is not None
            and context.runtime.container.contains(
                Memory,
            )
        ):
            return context.runtime.container.resolve(
                Memory,
            )

        return Memory()

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return pipeline diagnostics.
        """

        return {
            "engine": type(
                self.engine,
            ).__name__,
            "engine_diagnostics": (
                self.engine.diagnostics()
            ),
        }