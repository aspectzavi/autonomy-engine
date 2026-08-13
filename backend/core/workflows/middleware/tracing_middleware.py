"""
Tracing middleware.

Produces workflow execution traces.

The middleware records the execution lifecycle and stores a
WorkflowTrace in the MiddlewareContext.

Future implementations may additionally support:

- OpenTelemetry spans
- Jaeger
- Zipkin
- distributed tracing
- nested workflow traces
"""

from __future__ import annotations

from backend.core.workflows.middleware.middleware_context import (
    MiddlewareContext,
)
from backend.core.workflows.middleware.workflow_middleware import (
    NextMiddleware,
    WorkflowMiddleware,
)
from backend.core.workflows.runtime_report import (
    RuntimeReport,
)
from backend.core.workflows.workflow_trace import (
    WorkflowTrace,
)


class TracingMiddleware(
    WorkflowMiddleware,
):
    """
    Default workflow tracing middleware.
    """

    TRACE_KEY = "workflow.trace"

    async def execute(
        self,
        context: MiddlewareContext,
        next_handler: NextMiddleware,
    ) -> RuntimeReport:
        """
        Produce a workflow execution trace.
        """

        trace = WorkflowTrace.start(
            workflow=context.workflow.name,
        )

        context.set(
            self.TRACE_KEY,
            trace,
        )

        try:
            report = await next_handler(
                context,
            )

            trace = trace.finish(
                successful=report.success,
            )

            context.set(
                self.TRACE_KEY,
                trace,
            )

            return report

        except Exception as exc:
            trace = trace.finish(
                successful=False,
            )

            metadata = dict(
                trace.metadata,
            )

            metadata["error"] = str(
                exc,
            )

            trace = WorkflowTrace(
                workflow=trace.workflow,
                started_at=trace.started_at,
                finished_at=trace.finished_at,
                successful=trace.successful,
                events=trace.events,
                metadata=metadata,
            )

            context.set(
                self.TRACE_KEY,
                trace,
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
                "produces_trace": True,
                "trace_key": (
                    self.TRACE_KEY
                ),
            },
        )

        return diagnostics