"""
Reasoner.

Public interface to the reasoning subsystem.

The Reasoner delegates reasoning requests to an underlying
ReasoningEngine while presenting a stable API to the remainder of the
autonomy engine.

This mirrors the architecture used by other core subsystems such as
Memory and Capabilities.
"""

from __future__ import annotations

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


class Reasoner:
    """
    High-level reasoning interface.
    """

    def __init__(
        self,
        *,
        engine: ReasoningEngine | None = None,
    ) -> None:
        self._engine = (
            engine
            or ReasoningEngine()
        )

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

        return await self.engine.reason(
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
        Return diagnostics.
        """

        return {
            "engine": (
                self.engine.__class__.__name__
            ),
            "engine_diagnostics": (
                self.engine.diagnostics()
            ),
        }