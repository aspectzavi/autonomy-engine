"""
Reasoning result.

Represents the immutable output produced by the reasoning subsystem.

A ReasoningResult encapsulates:

- the selected reasoning strategy
- the final decision
- the reasoning trace
- overall confidence
- optional rationale
- immutable metadata

It contains no mutable execution state.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from backend.core.reasoning.decision import Decision
from backend.core.reasoning.reasoning_trace import ReasoningTrace


@dataclass(frozen=True, slots=True)
class ReasoningResult:
    """
    Immutable reasoning result.
    """

    #
    # Strategy that produced the decision.
    #
    strategy: str

    #
    # Final decision.
    #
    decision: Decision

    #
    # Complete reasoning trace.
    #
    trace: ReasoningTrace

    #
    # Overall confidence.
    #
    confidence: float

    #
    # Optional human-readable rationale.
    #
    rationale: str = ""

    #
    # Additional metadata.
    #
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
        Whether the reasoning confidence is high.
        """

        return self.confidence >= 0.80

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

    @property
    def step_count(
        self,
    ) -> int:
        """
        Number of reasoning steps.
        """

        return self.trace.step_count

    @property
    def successful(
        self,
    ) -> bool:
        """
        Whether the reasoning process completed successfully.
        """

        return self.trace.success

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
            "decision": self.decision.outcome,
            "decision_confidence": (
                self.decision.confidence
            ),
            "step_count": self.step_count,
            "successful": self.successful,
            "trace_completed": (
                self.trace.completed
            ),
            "rationale_length": len(
                self.rationale,
            ),
            "metadata_keys": tuple(
                sorted(
                    self.metadata.keys(),
                ),
            ),
        }