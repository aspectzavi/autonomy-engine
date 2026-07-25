"""
Episodic memory.

Stores experiences that occurred during execution.

Unlike semantic memory, episodic memory preserves events in temporal
order. It is intended to record goals, plans, observations, actions,
errors, and execution outcomes.

Future implementations may support:

- experience replay
- reflection
- self-improvement
- long-term learning
"""

from __future__ import annotations

from backend.core.memory.memory_store import MemoryStore


class EpisodicMemory(MemoryStore):
    """
    Episodic memory implementation.

    Currently this class extends the in-memory store without changing
    storage behavior. Future revisions will organize memories into
    execution episodes and support replay.
    """

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Episodic memory diagnostics.
        """

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "memory_type": "episodic",
                "episodes": False,
            },
        )

        return diagnostics