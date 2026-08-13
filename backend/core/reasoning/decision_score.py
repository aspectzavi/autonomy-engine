"""
Decision scoring.

Computes confidence scores for reasoning decisions.

The scorer combines multiple normalized signals into a single confidence
value between 0.0 and 1.0.

Current signals include:

- evidence quality
- strategy confidence
- memory support

Future versions may additionally incorporate:

- LLM confidence
- execution history
- tool reliability
- self-consistency
- voting among multiple reasoners
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class DecisionScore:
    """
    Confidence score produced by the reasoning subsystem.
    """

    confidence: float

    evidence_score: float

    strategy_score: float

    memory_score: float

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_high_confidence(
        self,
    ) -> bool:
        """
        Whether the score is considered high confidence.
        """

        return self.confidence >= 0.80

    @property
    def is_medium_confidence(
        self,
    ) -> bool:
        """
        Whether the score is considered medium confidence.
        """

        return (
            0.50
            <= self.confidence
            < 0.80
        )

    @property
    def is_low_confidence(
        self,
    ) -> bool:
        """
        Whether the score is considered low confidence.
        """

        return self.confidence < 0.50

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return score diagnostics.
        """

        return {
            "confidence": self.confidence,
            "evidence_score": self.evidence_score,
            "strategy_score": self.strategy_score,
            "memory_score": self.memory_score,
        }


class DecisionScorer:
    """
    Computes decision confidence.
    """

    #
    # Weighting factors.
    #
    EVIDENCE_WEIGHT = 0.40
    STRATEGY_WEIGHT = 0.35
    MEMORY_WEIGHT = 0.25

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    def score(
        self,
        *,
        evidence_score: float,
        strategy_score: float,
        memory_score: float,
    ) -> DecisionScore:
        """
        Compute a normalized decision confidence score.
        """

        evidence = self._normalize(
            evidence_score,
        )

        strategy = self._normalize(
            strategy_score,
        )

        memory = self._normalize(
            memory_score,
        )

        confidence = (
            evidence * self.EVIDENCE_WEIGHT
            + strategy * self.STRATEGY_WEIGHT
            + memory * self.MEMORY_WEIGHT
        )

        return DecisionScore(
            confidence=confidence,
            evidence_score=evidence,
            strategy_score=strategy,
            memory_score=memory,
        )

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _normalize(
        self,
        value: float,
    ) -> float:
        """
        Clamp a score into the range [0.0, 1.0].
        """

        if value < 0.0:
            return 0.0

        if value > 1.0:
            return 1.0

        return value

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return scorer diagnostics.
        """

        return {
            "component": "DecisionScorer",
            "weights": {
                "evidence": self.EVIDENCE_WEIGHT,
                "strategy": self.STRATEGY_WEIGHT,
                "memory": self.MEMORY_WEIGHT,
            },
        }