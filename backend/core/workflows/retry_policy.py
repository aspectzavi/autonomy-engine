"""
Retry policy.

Defines the interface responsible for determining whether a failed
workflow execution should be retried.

A RetryPolicy combines:

- failure classification
- retry attempt count
- execution context

to produce an immutable RetryDecision.

Concrete implementations may support deterministic rules, exponential
backoff, adaptive retry strategies, circuit breakers, or ML-driven
policies.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from backend.core.tasks.context import TaskContext
from backend.core.workflows.retry_decision import (
    RetryDecision,
)


class RetryPolicy(ABC):
    """
    Base interface for retry policies.
    """

    @abstractmethod
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

        Args:
            error:
                Exception that caused execution failure.

            attempt:
                Current attempt number (starting at 1).

            max_attempts:
                Maximum permitted attempts.

            context:
                Current task execution context.

        Returns:
            Immutable retry decision.
        """

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return retry policy diagnostics.
        """

        return {
            "policy": self.__class__.__name__,
        }