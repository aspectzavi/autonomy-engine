"""
Runtime tracing middleware.

Creates and manages execution traces around runtime requests.

This middleware connects the execution pipeline with the observability
layer and provides visibility into:

- request execution lifecycle
- execution duration
- failures
- trace identifiers
"""

from __future__ import annotations

from backend.core.observability.tracing import Tracing
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


class TracingMiddleware(RuntimeMiddleware):
    """
    Adds execution tracing to runtime requests.
    """

    def __init__(
        self,
        tracing: Tracing,
    ) -> None:
        self._tracing = tracing

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
        Execute request with tracing enabled.
        """

        trace = self._tracing.create_trace()

        context.set(
            "trace_id",
            trace.trace_id,
        )

        span = trace.start_span(
            "execution",
            metadata={
                "request_id": request.request_id,
                "goal": request.goal.description,
            },
        )

        try:
            result = await call_next(
                request,
            )

            span.set_metadata(
                "success",
                result.success,
            )

            span.finish()

            return result

        except Exception as exc:
            span.fail(
                exc,
            )

            raise

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return middleware diagnostics.
        """

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "tracing_enabled": True,
            }
        )

        return diagnostics