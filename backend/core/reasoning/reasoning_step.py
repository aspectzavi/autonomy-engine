"""
Reasoning step.

Represents a single step executed by the reasoning engine.

A reasoning process is composed of one or more reasoning steps.
Each step captures:

- what operation was performed
- its outcome
- confidence
- optional observations
- execution timing

ReasoningStep is immutable.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from datetime import UTC
from datetime import datetime
from typing import Any
from uuid import uuid4


@dataclass(slots=True, frozen=True)
class ReasoningStep:
    """
    Immutable reasoning step.
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
    # Step name.
    #
    name: str = ""

    #
    # Human-readable description.
    #
    description: str = ""

    #
    # Operation performed.
    #
    operation: str = ""

    #
    # Whether the step completed successfully.
    #
    success: bool = True

    #
    # Confidence assigned to this step.
    #
    confidence: float = 0.0

    #
    # Optional observations generated during execution.
    #
    observations: tuple[str, ...] = ()

    #
    # Arbitrary structured metadata.
    #
    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    #
    # Step start time.
    #
    started_at: datetime = field(
        default_factory=lambda: datetime.now(
            UTC,
        ),
    )

    #
    # Step completion time.
    #
    finished_at: datetime | None = None

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def completed(
        self,
    ) -> bool:
        """
        Whether the step completed.
        """

        return self.finished_at is not None

    @property
    def duration_seconds(
        self,
    ) -> float | None:
        """
        Duration of the reasoning step.
        """

        if self.finished_at is None:
            return None

        return (
            self.finished_at
            - self.started_at
        ).total_seconds()

    @property
    def has_observations(
        self,
    ) -> bool:
        """
        Whether observations were recorded.
        """

        return bool(
            self.observations,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return step diagnostics.
        """

        return {
            "id": self.id,
            "name": self.name,
            "operation": self.operation,
            "success": self.success,
            "confidence": self.confidence,
            "completed": self.completed,
            "duration_seconds": (
                self.duration_seconds
            ),
            "observations": len(
                self.observations,
            ),
            "metadata": self.metadata,
            "started_at": (
                self.started_at.isoformat()
            ),
            "finished_at": (
                None
                if self.finished_at is None
                else self.finished_at.isoformat()
            ),
        }