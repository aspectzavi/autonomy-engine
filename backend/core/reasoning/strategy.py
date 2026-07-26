"""
Reasoning strategy.

Defines the contract implemented by all reasoning strategies.

A strategy is responsible for analyzing a reasoning request and
producing a reasoning result.

Examples:

- HeuristicReasoner
- LLMReasoner
- TreeSearchReasoner
- MultiAgentReasoner
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from backend.core.reasoning.reasoning_context import (
    ReasoningContext,
)
from backend.core.reasoning.reasoning_request import (
    ReasoningRequest,
)
from backend.core.reasoning.reasoning_result import (
    ReasoningResult,
)


class Strategy(ABC):
    """
    Abstract reasoning strategy.
    """

    # ------------------------------------------------------------------
    # Reasoning
    # ------------------------------------------------------------------

    @abstractmethod
    async def reason(
        self,
        request: ReasoningRequest,
        context: ReasoningContext,
    ) -> ReasoningResult:
        """
        Execute reasoning.
        """

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    @abstractmethod
    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return strategy diagnostics.
        """