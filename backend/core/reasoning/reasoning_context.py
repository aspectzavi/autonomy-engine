"""
Reasoning context.

Provides shared services and runtime state required during reasoning.

The context is passed to every reasoning strategy and engine,
allowing implementations to access memory, capabilities,
observability, and future runtime services without introducing
tight coupling.
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.core.memory.memory import Memory
from backend.core.observability.events import EventBus


@dataclass(slots=True)
class ReasoningContext:
    """
    Runtime context supplied to the reasoning subsystem.
    """

    memory: Memory

    events: EventBus

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return context diagnostics.
        """

        return {
            "memory": (
                self.memory.__class__.__name__
            ),
            "events": (
                self.events.__class__.__name__
            ),
        }