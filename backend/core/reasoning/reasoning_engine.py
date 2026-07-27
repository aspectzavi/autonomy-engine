"""
Reasoning engine.

Coordinates execution of the reasoning subsystem.

The engine is responsible for:

- selecting a reasoning strategy
- executing the selected reasoner
- producing a ReasoningResult
- exposing diagnostics

Strategies remain independently replaceable.
"""

from __future__ import annotations

from backend.core.reasoning.heuristic_reasoner import (
    HeuristicReasoner,
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
from backend.core.reasoning.strategy_registry import (
    StrategyRegistry,
)


class ReasoningEngine:
    """
    Coordinates execution of the reasoning subsystem.
    """

    DEFAULT_STRATEGY = "heuristic"

    def __init__(
        self,
        *,
        registry: StrategyRegistry | None = None,
    ) -> None:
        self._registry = (
            registry
            if registry is not None
            else StrategyRegistry()
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
        Registered reasoning strategies.
        """

        return self._registry

    # ------------------------------------------------------------------
    # Strategy resolution
    # ------------------------------------------------------------------

    def strategy(
        self,
        name: str | None = None,
    ) -> Reasoner:
        """
        Resolve a reasoning strategy.

        If no strategy name is supplied, the default strategy is used.
        """

        return self.registry.strategy(
            name
            or self.DEFAULT_STRATEGY,
        )

    # ------------------------------------------------------------------
    # Reasoning
    # ------------------------------------------------------------------

    async def reason(
        self,
        request: ReasoningRequest,
        context: ReasoningContext,
        *,
        strategy: str | None = None,
    ) -> ReasoningResult:
        """
        Execute reasoning using the selected strategy.
        """

        reasoner = self.strategy(
            strategy,
        )

        return await reasoner.reason(
            request=request,
            context=context,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return engine diagnostics.
        """

        return {
            "default_strategy": (
                self.DEFAULT_STRATEGY
            ),
            "registered_strategies": (
                self.registry.names
            ),
            "registry": (
                self.registry.diagnostics()
            ),
        }