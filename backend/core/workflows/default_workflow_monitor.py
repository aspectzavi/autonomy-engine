"""
Default workflow monitor.

Production-ready implementation of WorkflowMonitor.

The default monitor collects execution metrics and execution traces for
a workflow without affecting execution.

Future implementations may integrate with:

- OpenTelemetry
- Prometheus
- Jaeger
- Grafana
- cloud monitoring backends
"""

from __future__ import annotations

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
    ) -> None:
        self._metrics = WorkflowMetrics()

        self._trace = WorkflowTrace()

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
            },
        )

        return diagnostics