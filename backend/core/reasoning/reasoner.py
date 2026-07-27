"""
Reasoner interface.

Defines the contract implemented by all reasoning strategies.

A Reasoner is responsible for transforming a ReasoningRequest and its
ReasoningContext into a structured ReasoningResult.

Implementations may include:

- heuristic reasoning
- LLM-based reasoning
- hybrid reasoning
- tree-search reasoning
- reflection-based reasoning

The Reasoner interface intentionally contains no implementation details,
allowing strategies to evolve independently of the reasoning engine.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from backend.core.reasoning.reasoning_context import (
    ReasoningContext,
)
from backend.core.reasoning.reasoning_request import (
    ReasoningRequest,
)
from backend.core.reasoning.reasoning_result import (
    ReasoningResult,
)


class Reasoner(ABC):
    """
    Base interface for all reasoning strategies.
    """

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    @abstractmethod
    def name(
        self,
    ) -> str:
        """
        Human-readable strategy name.
        """

    @property
    def description(
        self,
    ) -> str:
        """
        Human-readable strategy description.
        """

        return self.__class__.__doc__ or ""

    # ------------------------------------------------------------------
    # Capability
    # ------------------------------------------------------------------

    def supports(
        self,
        request: ReasoningRequest,
    ) -> bool:
        """
        Whether this reasoner can process the supplied request.

        The default implementation accepts every request.
        """

        del request

        return True

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
        Execute reasoning and produce a structured result.
        """

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return reasoner diagnostics.
        """

        return {
            "name": self.name,
            "description": self.description,
            "type": type(self).__name__,
        }