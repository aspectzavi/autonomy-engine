"""
Runtime metrics middleware.

Collects execution statistics across runtime requests.

Tracks:

- total executions
- successful executions
- failed executions
- total execution duration
- average execution duration

The middleware observes execution behavior without changing the
execution flow.
"""

from __future__ import annotations

from datetime import UTC, datetime

from backend.core.runtime.execution_request import (
    ExecutionRequest,
)
from backend.core.runtime.execution_result import (
    ExecutionResult,
)
from backend.core.runtime.middleware import (
    NextMiddleware,
    RuntimeMiddleware,
)
from backend.core.runtime.middleware_context import (
    MiddlewareContext,
)


class MetricsMiddleware(RuntimeMiddleware):
    """
    Collects runtime execution metrics.
    """

    def __init__(
        self,
    ) -> None:
        self._executions = 0
        self._successes = 0
        self._failures = 0
        self._total_duration = 0.0

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def invoke(
        self,
        context: MiddlewareContext,
        request: ExecutionRequest,
        call_next: NextMiddleware,
    ) -> ExecutionResult:
        """
        Execute request while collecting metrics.
        """

        started_at = datetime.now(
            UTC,
        )

        self._executions += 1

        try:
            result = await call_next(
                request,
            )

            if result.success:
                self._successes += 1
            else:
                self._failures += 1

            return result

        except Exception:
            self._failures += 1
            raise

        finally:
            finished_at = datetime.now(
                UTC,
            )

            duration = (
                finished_at - started_at
            ).total_seconds()

            self._total_duration += duration

            context.set(
                "execution_duration",
                duration,
            )

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    @property
    def executions(
        self,
    ) -> int:
        """
        Total execution count.
        """
        return self._executions

    @property
    def successes(
        self,
    ) -> int:
        """
        Successful execution count.
        """
        return self._successes

    @property
    def failures(
        self,
    ) -> int:
        """
        Failed execution count.
        """
        return self._failures

    @property
    def average_duration(
        self,
    ) -> float:
        """
        Average execution duration.
        """
        if self._executions == 0:
            return 0.0

        return (
            self._total_duration
            /
            self._executions
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return metrics diagnostics.
        """

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "executions": self.executions,
                "successes": self.successes,
                "failures": self.failures,
                "average_duration": (
                    self.average_duration
                ),
            }
        )

        return diagnostics