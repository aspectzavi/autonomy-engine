"""
Reasoning result.

Represents the immutable output produced by the reasoning subsystem.

A ReasoningResult describes the selected strategy, confidence, and
supporting rationale that will guide planning.

The result contains no mutable execution state.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ReasoningResult:
    """
    Immutable reasoning result.
    """

    strategy: str

    confidence: float

    rationale: str

    metadata: dict[str, object] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_confident(
        self,
    ) -> bool:
        """
        Whether the reasoning confidence is considered high.
        """

        return self.confidence >= 0.8

    @property
    def has_metadata(
        self,
    ) -> bool:
        """
        Whether metadata exists.
        """

        return bool(
            self.metadata,
        )

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def metadata_value(
        self,
        key: str,
        default: object | None = None,
    ) -> object | None:
        """
        Retrieve a metadata value.
        """

        return self.metadata.get(
            key,
            default,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return reasoning diagnostics.
        """

        return {
            "strategy": self.strategy,
            "confidence": self.confidence,
            "is_confident": self.is_confident,
            "rationale_length": len(
                self.rationale,
            ),
            "metadata_keys": tuple(
                sorted(
                    self.metadata.keys(),
                ),
            ),
        }