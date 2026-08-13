"""
Reasoning decision.

Represents the outcome of a reasoning process.

A Decision captures what the reasoning engine concluded, together with
its confidence, supporting rationale, and optional metadata that may be
used by downstream components.

A Decision is intentionally immutable.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from datetime import UTC
from datetime import datetime
from typing import Any
from uuid import uuid4


@dataclass(slots=True, frozen=True)
class Decision:
    """
    Immutable reasoning decision.
    """

    #
    # Unique identifier.
    #
    id: str = field(
        default_factory=lambda: str(
            uuid4(),
        ),
    )

    #
    # Decision label.
    #
    name: str = ""

    #
    # Human-readable description.
    #
    description: str = ""

    #
    # Final decision value.
    #
    outcome: str = ""

    #
    # Confidence score.
    #
    confidence: float = 0.0

    #
    # Optional supporting evidence.
    #
    evidence: tuple[str, ...] = ()

    #
    # Optional recommendations.
    #
    recommendations: tuple[str, ...] = ()

    #
    # Additional structured metadata.
    #
    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    #
    # Creation timestamp.
    #
    created_at: datetime = field(
        default_factory=lambda: datetime.now(
            UTC,
        ),
    )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_confident(
        self,
    ) -> bool:
        """
        Whether the decision is considered confident.
        """

        return self.confidence >= 0.80

    @property
    def has_evidence(
        self,
    ) -> bool:
        """
        Whether supporting evidence exists.
        """

        return bool(
            self.evidence,
        )

    @property
    def has_recommendations(
        self,
    ) -> bool:
        """
        Whether follow-up recommendations exist.
        """

        return bool(
            self.recommendations,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return decision diagnostics.
        """

        return {
            "id": self.id,
            "name": self.name,
            "outcome": self.outcome,
            "confidence": self.confidence,
            "confident": self.is_confident,
            "evidence_count": len(
                self.evidence,
            ),
            "recommendation_count": len(
                self.recommendations,
            ),
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }