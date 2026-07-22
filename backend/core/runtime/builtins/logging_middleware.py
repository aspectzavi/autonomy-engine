"""
Runtime logging middleware.

Provides structured execution logging around runtime requests.

Responsibilities:

- log execution start
- log selected request information
- log execution completion
- log execution failures

The middleware does not alter execution behavior. It only observes
runtime execution.
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


class LoggingMiddleware(RuntimeMiddleware):
    """
    Logs runtime execution lifecycle events.
    """

    async def invoke(
        self,
        context: MiddlewareContext,
        request: ExecutionRequest,
        call_next: NextMiddleware,
    ) -> ExecutionResult:
        """
        Execute request with logging around the pipeline.
        """

        started_at = datetime.now(
            UTC,
        )

        context.set(
            "execution_started_at",
            started_at,
        )

        print(
            "[Runtime] Execution started:",
            request.request_id,
        )

        print(
            "[Runtime] Goal:",
            request.goal.description,
        )

        try:
            result = await call_next(
                request,
            )

            finished_at = datetime.now(
                UTC,
            )

            duration = (
                finished_at - started_at
            ).total_seconds()

            context.set(
                "execution_duration",
                duration,
            )

            print(
                "[Runtime] Execution completed:",
                request.request_id,
                f"({duration:.3f}s)",
            )

            return result

        except Exception as exc:
            finished_at = datetime.now(
                UTC,
            )

            duration = (
                finished_at - started_at
            ).total_seconds()

            context.set(
                "execution_duration",
                duration,
            )

            print(
                "[Runtime] Execution failed:",
                request.request_id,
                f"({duration:.3f}s)",
                str(exc),
            )

            raise

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return middleware diagnostics.
        """

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "logging": True,
                "mode": "console",
            }
        )

        return diagnostics