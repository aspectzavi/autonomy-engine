"""
Reasoning engine.

Coordinates execution of the reasoning subsystem.

The engine delegates reasoning requests to registered strategies.

Initially the engine selects the default heuristic strategy. Future
implementations may dynamically select strategies based on the request,
runtime policy, or available AI providers.
"""

from __future__ import annotations

from backend.core.reasoning.heuristic_reasoner import (
    HeuristicReasoner,
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
from backend.core.reasoning.strategy_registry import (
    StrategyRegistry,
)


class ReasoningEngine:
    """
    Default reasoning engine.
    """

    DEFAULT_STRATEGY = "heuristic"

    def __init__(
        self,
        *,
        registry: StrategyRegistry | None = None,
    ) -> None:
        self._registry = (
            registry
            or StrategyRegistry()
        )

        if not self._registry.contains(
            self.DEFAULT_STRATEGY,
        ):
            self._registry.register(
                name=self.DEFAULT_STRATEGY,
                strategy=HeuristicReasoner(),
            )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def registry(
        self,
    ) -> StrategyRegistry:
        """
        Strategy registry.
        """

        return self._registry

    # ------------------------------------------------------------------
    # Reasoning
    # ------------------------------------------------------------------

    async def reason(
        self,
        request: ReasoningRequest,
        context: ReasoningContext,
    ) -> ReasoningResult:
        """
        Execute reasoning.
        """

        strategy = self.registry.strategy(
            self.DEFAULT_STRATEGY,
        )

        return await strategy.reason(
            request,
            context,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Engine diagnostics.
        """

        return {
            "default_strategy": (
                self.DEFAULT_STRATEGY
            ),
            "registry": (
                self.registry.diagnostics()
            ),
        }