"""
Default workflow monitor.

Production-ready implementation of WorkflowMonitor.

The default monitor collects execution metrics and execution traces for
a workflow without affecting execution. It also opens a real
observability span through the shared Tracing service, so a workflow
execution is visible alongside every other traced operation in the
system (agents, tools, planning) rather than only inside its own
isolated WorkflowTrace record.

Future implementations may integrate with:

- OpenTelemetry
- Prometheus
- Jaeger
- Grafana
- cloud monitoring backends
"""

from __future__ import annotations

from backend.core.observability.execution_trace import (
    ExecutionTrace,
)
from backend.core.observability.trace_span import (
    TraceSpan,
)
from backend.core.observability.tracing import (
    Tracing,
)
from backend.core.workflows.execution_result import (
    ExecutionResult,
)
from backend.core.workflows.workflow import (
    Workflow,
)
from backend.core.workflows.workflow_metrics import (
    WorkflowMetrics,
)
from backend.core.workflows.workflow_monitor import (
    WorkflowMonitor,
)
from backend.core.workflows.workflow_trace import (
    WorkflowTrace,
)


class DefaultWorkflowMonitor(
    WorkflowMonitor,
):
    """
    Default workflow monitor.
    """

    def __init__(
        self,
        *,
        tracing: Tracing,
    ) -> None:
        self._tracing = tracing

        self._metrics = WorkflowMetrics()

        self._trace = WorkflowTrace()

        self._execution_trace: ExecutionTrace | None = None

        self._root_span: TraceSpan | None = None

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def current_metrics(
        self,
    ) -> WorkflowMetrics:
        """
        Current metrics snapshot.
        """

        return self._metrics

    @property
    def current_trace(
        self,
    ) -> WorkflowTrace:
        """
        Current execution trace.
        """

        return self._trace

    @property
    def execution_trace(
        self,
    ) -> ExecutionTrace | None:
        """
        Shared observability trace opened for this workflow run, if
        monitoring has begun.
        """

        return self._execution_trace

    # ------------------------------------------------------------------
    # Monitoring
    # ------------------------------------------------------------------

    async def begin(
        self,
        *,
        workflow: Workflow,
    ) -> None:
        """
        Begin monitoring.
        """

        self._trace = WorkflowTrace.start(
            workflow=workflow.name,
        )

        self._execution_trace = (
            self._tracing.create_trace()
        )

        self._root_span = (
            self._execution_trace.start_span(
                f"workflow.{workflow.name}",
                metadata={
                    "workflow": workflow.name,
                },
            )
        )

    async def finish(
        self,
        *,
        workflow: Workflow,
        result: ExecutionResult,
    ) -> None:
        """
        Finish monitoring.
        """

        self._metrics = WorkflowMetrics(
            workflow=workflow.name,
            successful=result.success,
            completed_batches=result.completed_batches,
            completed_tasks=result.completed_tasks,
            failed_tasks=result.failed_tasks,
            metadata=result.metadata,
        )

        self._trace = self._trace.finish(
            successful=result.success,
        )

        if self._root_span is not None:
            self._root_span.set_metadata(
                "completed_batches",
                result.completed_batches,
            )

            self._root_span.set_metadata(
                "completed_tasks",
                result.completed_tasks,
            )

            self._root_span.set_metadata(
                "failed_tasks",
                result.failed_tasks,
            )

            if result.success:
                self._root_span.finish()
            else:
                self._root_span.fail(
                    f"{result.failed_tasks} task(s) failed",
                )

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def metrics(
        self,
    ) -> WorkflowMetrics:
        """
        Return workflow metrics.
        """

        return self.current_metrics

    def trace(
        self,
    ) -> WorkflowTrace:
        """
        Return workflow trace.
        """

        return self.current_trace

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return monitor diagnostics.
        """

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "metrics": (
                    self.current_metrics.diagnostics()
                ),
                "trace": (
                    self.current_trace.diagnostics()
                ),
                "execution_trace_id": (
                    self._execution_trace.trace_id
                    if self._execution_trace is not None
                    else None
                ),
            },
        )

        return diagnostics