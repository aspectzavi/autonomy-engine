"""
Resilience report.

Represents the immutable outcome of the workflow resilience subsystem.

A ResilienceReport summarizes the resilience actions taken while
executing a workflow, including retries, cancellations, timeout
handling, and future recovery strategies.

The report intentionally contains no runtime behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


@dataclass(
    frozen=True,
    slots=True,
)
class ResilienceReport:
    """
    Immutable workflow resilience report.
    """

    successful: bool

    retry_attempts: int = 0

    retries_performed: int = 0

    timed_out: bool = False

    cancelled: bool = False

    recovered: bool = False

    failure_classification: str | None = None

    metadata: dict[str, object] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def has_retries(
        self,
    ) -> bool:
        """
        Whether any retry attempts occurred.
        """

        return self.retries_performed > 0

    @property
    def exhausted_retries(
        self,
    ) -> bool:
        """
        Whether every available retry attempt was consumed.
        """

        return (
            self.retry_attempts > 0
            and self.retries_performed >= self.retry_attempts
        )

    @property
    def interrupted(
        self,
    ) -> bool:
        """
        Whether execution was interrupted.
        """

        return (
            self.timed_out
            or self.cancelled
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return resilience diagnostics.
        """

        return {
            "successful": self.successful,
            "retry_attempts": (
                self.retry_attempts
            ),
            "retries_performed": (
                self.retries_performed
            ),
            "has_retries": (
                self.has_retries
            ),
            "exhausted_retries": (
                self.exhausted_retries
            ),
            "timed_out": (
                self.timed_out
            ),
            "cancelled": (
                self.cancelled
            ),
            "interrupted": (
                self.interrupted
            ),
            "recovered": (
                self.recovered
            ),
            "failure_classification": (
                self.failure_classification
            ),
            "metadata": (
                self.metadata
            ),
        }