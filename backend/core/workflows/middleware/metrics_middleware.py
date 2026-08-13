"""
Metrics middleware.

Produces immutable WorkflowMetrics after workflow execution.

The middleware stores the resulting WorkflowMetrics in the
MiddlewareContext for downstream middleware and the runtime.

Future implementations may additionally support:

- Prometheus exporters
- OpenTelemetry metrics
- latency histograms
- distributed aggregation
"""

from __future__ import annotations

from backend.core.workflows.execution_result import (
    ExecutionResult,
)
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
from backend.core.workflows.workflow_metrics import (
    WorkflowMetrics,
)


class MetricsMiddleware(
    WorkflowMiddleware,
):
    """
    Default workflow metrics middleware.
    """

    METRICS_KEY = "workflow.metrics"

    async def execute(
        self,
        context: MiddlewareContext,
        next_handler: NextMiddleware,
    ) -> RuntimeReport:
        """
        Produce workflow metrics.
        """

        report = await next_handler(
            context,
        )

        execution = context.get(
            "workflow.execution_result",
        )

        if isinstance(
            execution,
            ExecutionResult,
        ):
            metrics = WorkflowMetrics(
                workflow=context.workflow.name,
                successful=report.success,
                completed_batches=(
                    execution.completed_batches
                ),
                completed_tasks=(
                    execution.completed_tasks
                ),
                failed_tasks=(
                    execution.failed_tasks
                ),
            )
        else:
            #
            # Executor did not expose detailed execution data.
            #
            metrics = WorkflowMetrics(
                workflow=context.workflow.name,
                successful=report.success,
            )

        context.set(
            self.METRICS_KEY,
            metrics,
        )

        return report

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
                "produces_metrics": True,
                "metrics_key": (
                    self.METRICS_KEY
                ),
            },
        )

        return diagnostics