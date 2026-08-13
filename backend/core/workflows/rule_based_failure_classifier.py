
"""
Rule-based workflow failure classifier.

Provides deterministic failure classification for the workflow
resilience subsystem.

The classifier intentionally contains no retry policy. It only
classifies exceptions so that RetryPolicy can make the retry decision.
"""

from __future__ import annotations

import asyncio
from concurrent.futures import CancelledError as FuturesCancelledError

from backend.core.workflows.failure_classifier import (
    FailureClassifier,
)


class RuleBasedFailureClassifier(
    FailureClassifier,
):
    """
    Deterministic workflow failure classifier.

    Classification values are stable strings consumed by retry
    policies and resilience components.
    """

    TRANSIENT = "transient"
    PERMANENT = "permanent"
    TIMEOUT = "timeout"
    CANCELLATION = "cancellation"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    EXTERNAL_SERVICE = "external_service"

    def classify(
        self,
        error: Exception,
    ) -> str:
        """
        Classify an execution failure using deterministic rules.
        """

        if isinstance(
            error,
            (
                asyncio.CancelledError,
                FuturesCancelledError,
            ),
        ):
            return self.CANCELLATION

        if isinstance(
            error,
            (
                TimeoutError,
                asyncio.TimeoutError,
            ),
        ):
            return self.TIMEOUT

        if isinstance(
            error,
            (
                MemoryError,
            ),
        ):
            return self.RESOURCE_EXHAUSTION

        #
        # Common external-service/network failures.
        #
        if isinstance(
            error,
            (
                ConnectionError,
            ),
        ):
            return self.EXTERNAL_SERVICE

        #
        # Errors that commonly indicate temporary resource or
        # availability problems.
        #
        transient_names = {
            "BusyError",
            "ConnectionResetError",
            "ConnectionRefusedError",
            "TemporaryError",
            "TemporaryFailure",
            "ServiceUnavailableError",
            "TooManyRequestsError",
        }

        if type(error).__name__ in transient_names:
            return self.TRANSIENT

        #
        # Default to permanent. This is intentionally conservative:
        # unknown failures should not automatically trigger retries.
        #
        return self.PERMANENT

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return classifier diagnostics.
        """

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "strategy": "rule_based",
                "classifications": (
                    self.TRANSIENT,
                    self.PERMANENT,
                    self.TIMEOUT,
                    self.CANCELLATION,
                    self.RESOURCE_EXHAUSTION,
                    self.EXTERNAL_SERVICE,
                ),
            }
        )

        return diagnostics