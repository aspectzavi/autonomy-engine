"""
Capability match.

Represents a single capability selected during planning together with
the confidence and rationale behind the selection.

CapabilityMatch objects are produced by CapabilitySelector
implementations and can later support ranking, semantic search,
learning-based planning, and explainability.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


@dataclass(
    frozen=True,
    slots=True,
)
class CapabilityMatch:
    """
    Immutable capability selection.
    """

    capability: str

    score: float

    reason: str = ""

    metadata: dict[str, object] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_high_confidence(
        self,
    ) -> bool:
        """
        Whether this capability was selected with high confidence.
        """

        return self.score >= 0.80

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return capability match diagnostics.
        """

        return {
            "capability": self.capability,
            "score": self.score,
            "high_confidence": (
                self.is_high_confidence
            ),
            "reason": self.reason,
            "metadata": self.metadata,
        }