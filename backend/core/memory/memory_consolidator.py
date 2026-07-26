"""
Memory consolidator.

Consolidates related memories into a smaller set of higher-value
memories.

Without consolidation, long-running autonomous systems eventually
accumulate thousands of repetitive experiences.

The consolidator reduces memory growth by merging duplicate or highly
similar memories.

The current implementation performs deterministic duplicate removal.

Future implementations may:

- summarize repeated experiences
- merge semantically similar memories
- build long-term knowledge
- detect recurring failures
- generate episodic summaries
- invoke an LLM for abstraction
"""

from __future__ import annotations

from backend.core.memory.memory_entry import MemoryEntry


class MemoryConsolidator:
    """
    Consolidates memory collections.
    """

    def consolidate(
        self,
        entries: list[MemoryEntry],
    ) -> list[MemoryEntry]:
        """
        Consolidate a collection of memories.

        Duplicate memories are removed while preserving the first
        occurrence.
        """

        seen: set[str] = set()

        consolidated: list[MemoryEntry] = []

        for entry in entries:
            signature = self._signature(
                entry,
            )

            if signature in seen:
                continue

            seen.add(
                signature,
            )

            consolidated.append(
                entry,
            )

        return consolidated

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _signature(
        self,
        entry: MemoryEntry,
    ) -> str:
        """
        Produce a deterministic signature for duplicate detection.

        Future implementations may replace this with semantic hashes or
        embedding-based clustering.
        """

        return (
            entry.content.strip()
            .lower()
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return consolidator diagnostics.
        """

        return {
            "component": "MemoryConsolidator",
            "strategy": "exact-content",
        }