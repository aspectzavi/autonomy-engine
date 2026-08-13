"""
Retry decision.

Represents the immutable decision produced by a RetryPolicy.

A RetryDecision answers whether execution should be retried and, if so,
under what conditions.

The object intentionally contains no retry logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


@dataclass(
    frozen=True,
    slots=True,
)
class RetryDecision:
    """
    Immutable retry decision.
    """

    should_retry: bool

    remaining_attempts: int = 0

    delay_seconds: float = 0.0

    reason: str = ""

    metadata: dict[str, object] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def exhausted(
        self,
    ) -> bool:
        """
        Whether all retry attempts have been exhausted.
        """

        return (
            not self.should_retry
            or self.remaining_attempts <= 0
        )

    @property
    def immediate(
        self,
    ) -> bool:
        """
        Whether retry should occur immediately.
        """

        return (
            self.should_retry
            and self.delay_seconds <= 0.0
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return retry diagnostics.
        """

        return {
            "should_retry": (
                self.should_retry
            ),
            "remaining_attempts": (
                self.remaining_attempts
            ),
            "delay_seconds": (
                self.delay_seconds
            ),
            "reason": (
                self.reason
            ),
            "exhausted": (
                self.exhausted
            ),
            "immediate": (
                self.immediate
            ),
            "metadata": (
                self.metadata
            ),
        }