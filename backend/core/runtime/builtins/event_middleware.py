"""
Runtime event middleware.

Publishes execution lifecycle events during runtime processing.

The middleware observes execution flow and emits events without
changing execution behavior.

Events are published through the RuntimeContext EventBus when
available.
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


class EventMiddleware(RuntimeMiddleware):
    """
    Publishes runtime execution events.
    """

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
        Execute request while publishing lifecycle events.
        """

        started_at = datetime.now(
            UTC,
        )

        self._publish(
            context,
            "execution.started",
            {
                "request_id": request.request_id,
                "correlation_id": (
                    context.correlation_id
                ),
                "goal": request.goal.description,
                "started_at": (
                    started_at.isoformat()
                ),
            },
        )

        try:
            result = await call_next(
                request,
            )

            finished_at = datetime.now(
                UTC,
            )

            self._publish(
                context,
                "execution.completed",
                {
                    "request_id": request.request_id,
                    "correlation_id": (
                        context.correlation_id
                    ),
                    "success": result.success,
                    "duration": (
                        finished_at - started_at
                    ).total_seconds(),
                },
            )

            return result

        except Exception as exc:
            finished_at = datetime.now(
                UTC,
            )

            self._publish(
                context,
                "execution.failed",
                {
                    "request_id": request.request_id,
                    "correlation_id": (
                        context.correlation_id
                    ),
                    "error": str(exc),
                    "duration": (
                        finished_at - started_at
                    ).total_seconds(),
                },
            )

            raise

    # ------------------------------------------------------------------
    # Event Publishing
    # ------------------------------------------------------------------

    def _publish(
        self,
        context: MiddlewareContext,
        event_name: str,
        payload: dict[str, object],
    ) -> None:
        """
        Publish runtime event if RuntimeContext is available.
        """

        if context.runtime is None:
            return

        events = context.runtime.events

        events.publish(
            event_name,
            payload,
        )

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
                "events": True,
                "source": "runtime_context",
            }
        )

        return diagnostics