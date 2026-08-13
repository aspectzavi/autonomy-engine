"""
Rule-based retry policy.

Default deterministic implementation of RetryPolicy.

The policy uses a FailureClassifier together with simple retry rules to
determine whether execution should be retried.

Current behavior:

- retry transient failures
- retry timeouts
- retry resource exhaustion
- never retry permanent failures
- never retry cancellations
- exponential backoff

Future implementations may support:

- adaptive backoff
- circuit breakers
- per-capability retry rules
- distributed retry coordination
- ML-based retry prediction
"""

from __future__ import annotations

from backend.core.tasks.context import TaskContext
from backend.core.workflows.failure_classifier import (
    FailureClassifier,
)
from backend.core.workflows.retry_decision import (
    RetryDecision,
)
from backend.core.workflows.retry_policy import (
    RetryPolicy,
)


class RuleBasedRetryPolicy(
    RetryPolicy,
):
    """
    Default deterministic retry policy.
    """

    def __init__(
        self,
        *,
        classifier: FailureClassifier,
        base_delay_seconds: float = 1.0,
    ) -> None:
        self._classifier = classifier
        self._base_delay_seconds = (
            base_delay_seconds
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def classifier(
        self,
    ) -> FailureClassifier:
        """
        Failure classifier.
        """

        return self._classifier

    @property
    def base_delay_seconds(
        self,
    ) -> float:
        """
        Initial retry delay.
        """

        return self._base_delay_seconds

    # ------------------------------------------------------------------
    # Retry Decision
    # ------------------------------------------------------------------

    async def decide(
        self,
        *,
        error: Exception,
        attempt: int,
        max_attempts: int,
        context: TaskContext,
    ) -> RetryDecision:
        """
        Determine whether execution should be retried.
        """

        if context.is_cancelled:
            return RetryDecision(
                should_retry=False,
                remaining_attempts=0,
                reason="execution cancelled",
            )

        classification = (
            self.classifier.classify(
                error,
            )
        )

        remaining = max(
            max_attempts - attempt,
            0,
        )

        if classification in (
            "permanent",
            "cancelled",
        ):
            return RetryDecision(
                should_retry=False,
                remaining_attempts=remaining,
                reason=classification,
                metadata={
                    "classification": (
                        classification
                    ),
                },
            )

        if remaining == 0:
            return RetryDecision(
                should_retry=False,
                remaining_attempts=0,
                reason="retry limit reached",
                metadata={
                    "classification": (
                        classification
                    ),
                },
            )

        delay = (
            self.base_delay_seconds
            * (2 ** (attempt - 1))
        )

        return RetryDecision(
            should_retry=True,
            remaining_attempts=remaining,
            delay_seconds=delay,
            reason=classification,
            metadata={
                "classification": (
                    classification
                ),
                "attempt": attempt,
                "max_attempts": (
                    max_attempts
                ),
            },
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return retry policy diagnostics.
        """

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "type": "rule-based",
                "classifier": (
                    self.classifier.diagnostics()
                ),
                "base_delay_seconds": (
                    self.base_delay_seconds
                ),
                "backoff": "exponential",
            },
        )

        return diagnostics