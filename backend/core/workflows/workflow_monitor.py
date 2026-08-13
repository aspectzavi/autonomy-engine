"""
Workflow monitor.

Defines the interface responsible for observing workflow execution.

The workflow monitor is purely observational. It receives workflow
execution events and produces metrics and traces without influencing
execution.

Responsibilities:

- monitor workflow lifecycle
- collect execution metrics
- build execution traces
- generate monitoring artifacts

Concrete implementations may additionally support:

- OpenTelemetry
- Prometheus
- distributed tracing
- performance analytics
- live dashboards
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from backend.core.workflows.execution_result import (
    ExecutionResult,
)
from backend.core.workflows.workflow import (
    Workflow,
)
from backend.core.workflows.workflow_metrics import (
    WorkflowMetrics,
)
from backend.core.workflows.workflow_trace import (
    WorkflowTrace,
)


class WorkflowMonitor(ABC):
    """
    Base interface for workflow monitoring.
    """

    @abstractmethod
    async def begin(
        self,
        *,
        workflow: Workflow,
    ) -> None:
        """
        Begin monitoring a workflow execution.
        """

    @abstractmethod
    async def finish(
        self,
        *,
        workflow: Workflow,
        result: ExecutionResult,
    ) -> None:
        """
        Finish monitoring a workflow execution.
        """

    @abstractmethod
    def metrics(
        self,
    ) -> WorkflowMetrics:
        """
        Return collected workflow metrics.
        """

    @abstractmethod
    def trace(
        self,
    ) -> WorkflowTrace:
        """
        Return the workflow execution trace.
        """

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return monitor diagnostics.
        """

        return {
            "monitor": self.__class__.__name__,
        }