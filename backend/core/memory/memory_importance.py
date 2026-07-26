"""
Memory importance.

Determines the relative importance of a memory entry.

Importance scores are used to guide:

- long-term retention
- semantic ranking
- consolidation
- forgetting
- summarization

The current implementation is deterministic and intentionally simple.
Future implementations may incorporate:

- LLM evaluation
- reinforcement signals
- user feedback
- execution frequency
- recency decay
- semantic novelty
"""

from __future__ import annotations

from backend.core.memory.memory_entry import MemoryEntry


class MemoryImportance:
    """
    Computes memory importance scores.
    """

    #
    # Score constants
    #
    LOW = 0.25
    NORMAL = 0.50
    HIGH = 0.75
    CRITICAL = 1.00

    def score(
        self,
        entry: MemoryEntry,
    ) -> float:
        """
        Compute an importance score for a memory.

        Returns a value in the range [0.0, 1.0].
        """

        metadata = entry.metadata

        #
        # Explicit importance always wins.
        #
        importance = metadata.get(
            "importance",
        )

        if isinstance(
            importance,
            (int, float),
        ):
            return max(
                0.0,
                min(
                    1.0,
                    float(importance),
                ),
            )

        #
        # Failed executions are more valuable than successful ones.
        #
        success = metadata.get(
            "success",
        )

        if success is False:
            return self.HIGH

        #
        # Critical memories.
        #
        if metadata.get(
            "critical",
            False,
        ):
            return self.CRITICAL

        #
        # Frequently accessed memories.
        #
        access_count = metadata.get(
            "access_count",
            0,
        )

        if (
            isinstance(access_count, int)
            and access_count >= 10
        ):
            return self.HIGH

        #
        # Long memories often contain richer context.
        #
        if len(entry.content) >= 500:
            return self.HIGH

        if len(entry.content) >= 150:
            return self.NORMAL + 0.10

        #
        # Default.
        #
        return self.NORMAL

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return scorer diagnostics.
        """

        return {
            "component": "MemoryImportance",
            "range": (
                0.0,
                1.0,
            ),
        }