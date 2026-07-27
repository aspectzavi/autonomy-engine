"""
Reasoning trace.

Represents the complete reasoning session executed by the reasoning
engine.

A ReasoningTrace records the sequence of ReasoningStep objects that led
to a final decision. It is intended for diagnostics, observability, and
telemetry—not for storing internal chain-of-thought.

The trace provides execution metadata such as:

- number of reasoning steps
- total duration
- average confidence
- overall success
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from datetime import UTC
from datetime import datetime
from statistics import mean
from typing import Any

from backend.core.reasoning.reasoning_step import ReasoningStep


@dataclass(slots=True)
class ReasoningTrace:
    """
    Complete reasoning trace.
    """

    #
    # Recorded reasoning steps.
    #
    steps: list[ReasoningStep] = field(
        default_factory=list,
    )

    #
    # Trace metadata.
    #
    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    #
    # Trace start time.
    #
    started_at: datetime = field(
        default_factory=lambda: datetime.now(
            UTC,
        ),
    )

    #
    # Trace completion time.
    #
    finished_at: datetime | None = None

    # ------------------------------------------------------------------
    # Step management
    # ------------------------------------------------------------------

    def add_step(
        self,
        step: ReasoningStep,
    ) -> None:
        """
        Record a reasoning step.
        """

        self.steps.append(
            step,
        )

    def finish(
        self,
    ) -> None:
        """
        Mark the reasoning trace as complete.
        """

        self.finished_at = datetime.now(
            UTC,
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def completed(
        self,
    ) -> bool:
        """
        Whether reasoning has completed.
        """

        return self.finished_at is not None

    @property
    def step_count(
        self,
    ) -> int:
        """
        Number of reasoning steps.
        """

        return len(
            self.steps,
        )

    @property
    def successful_steps(
        self,
    ) -> int:
        """
        Number of successful steps.
        """

        return sum(
            1
            for step in self.steps
            if step.success
        )

    @property
    def failed_steps(
        self,
    ) -> int:
        """
        Number of failed steps.
        """

        return self.step_count - self.successful_steps

    @property
    def success(
        self,
    ) -> bool:
        """
        Whether every reasoning step succeeded.
        """

        return all(
            step.success
            for step in self.steps
        )

    @property
    def average_confidence(
        self,
    ) -> float:
        """
        Mean confidence across all reasoning steps.
        """

        if not self.steps:
            return 0.0

        return mean(
            step.confidence
            for step in self.steps
        )

    @property
    def duration_seconds(
        self,
    ) -> float | None:
        """
        Total reasoning duration.
        """

        if self.finished_at is None:
            return None

        return (
            self.finished_at
            - self.started_at
        ).total_seconds()

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return reasoning trace diagnostics.
        """

        return {
            "completed": self.completed,
            "success": self.success,
            "step_count": self.step_count,
            "successful_steps": self.successful_steps,
            "failed_steps": self.failed_steps,
            "average_confidence": (
                self.average_confidence
            ),
            "duration_seconds": (
                self.duration_seconds
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