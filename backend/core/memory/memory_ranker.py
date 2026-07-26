"""
Memory ranker.

Ranks retrieved memories using multiple signals.

The ranker combines:

- semantic similarity
- memory importance
- recency
- access frequency

The current implementation is deterministic and uses weighted scoring.
Future implementations may use learned ranking models.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC
from datetime import datetime

from backend.core.memory.memory_entry import MemoryEntry
from backend.core.memory.memory_importance import (
    MemoryImportance,
)


@dataclass(slots=True, frozen=True)
class RankedMemory:
    """
    Memory together with its computed ranking score.
    """

    entry: MemoryEntry

    similarity: float

    importance: float

    recency: float

    score: float


class MemoryRanker:
    """
    Rank memories for retrieval.
    """

    #
    # Weighting factors.
    #
    SIMILARITY_WEIGHT = 0.60
    IMPORTANCE_WEIGHT = 0.25
    RECENCY_WEIGHT = 0.15

    def __init__(
        self,
        *,
        importance: MemoryImportance | None = None,
    ) -> None:
        self._importance = (
            importance
            if importance is not None
            else MemoryImportance()
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def importance(
        self,
    ) -> MemoryImportance:
        """
        Memory importance scorer.
        """
        return self._importance

    # ------------------------------------------------------------------
    # Ranking
    # ------------------------------------------------------------------

    def rank(
        self,
        *,
        entries: list[MemoryEntry],
        similarities: list[float],
    ) -> list[RankedMemory]:
        """
        Rank retrieved memories.

        The number of similarity scores must match the number of entries.
        """

        if len(entries) != len(similarities):
            raise ValueError(
                "Entries and similarities must have identical length."
            )

        ranked: list[RankedMemory] = []

        for entry, similarity in zip(
            entries,
            similarities,
        ):
            importance = self.importance.score(
                entry,
            )

            recency = self._recency_score(
                entry,
            )

            score = (
                similarity * self.SIMILARITY_WEIGHT
                + importance * self.IMPORTANCE_WEIGHT
                + recency * self.RECENCY_WEIGHT
            )

            ranked.append(
                RankedMemory(
                    entry=entry,
                    similarity=similarity,
                    importance=importance,
                    recency=recency,
                    score=score,
                )
            )

        ranked.sort(
            key=lambda item: item.score,
            reverse=True,
        )

        return ranked

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _recency_score(
        self,
        entry: MemoryEntry,
    ) -> float:
        """
        Compute a normalized recency score.

        Returns a value between 0.0 and 1.0.
        """

        timestamp = entry.metadata.get(
            "timestamp",
        )

        if not isinstance(
            timestamp,
            str,
        ):
            return 0.50

        try:
            created = datetime.fromisoformat(
                timestamp,
            )
        except ValueError:
            return 0.50

        age_days = (
            datetime.now(
                UTC,
            )
            - created
        ).total_seconds() / 86400.0

        if age_days <= 1:
            return 1.00

        if age_days <= 7:
            return 0.90

        if age_days <= 30:
            return 0.75

        if age_days <= 90:
            return 0.60

        return 0.40

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return ranker diagnostics.
        """

        return {
            "component": "MemoryRanker",
            "weights": {
                "similarity": self.SIMILARITY_WEIGHT,
                "importance": self.IMPORTANCE_WEIGHT,
                "recency": self.RECENCY_WEIGHT,
            },
            "importance": (
                self.importance.diagnostics()
            ),
        }