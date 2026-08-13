"""
Workflow runtime.

Defines the interface responsible for orchestrating workflow execution.

A WorkflowRuntime coordinates the complete runtime lifecycle:

    Workflow
        ↓
    WorkflowScheduler
        ↓
    SchedulingPlan
        ↓
    WorkflowExecutor
        ↓
    RuntimeReport

The runtime itself performs no scheduling or execution logic. It simply
coordinates the workflow components.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from backend.core.tasks.context import (
    TaskContext,
)
from backend.core.workflows.runtime_report import (
    RuntimeReport,
)
from backend.core.workflows.workflow import (
    Workflow,
)


class WorkflowRuntime(ABC):
    """
    Base workflow runtime.
    """

    @abstractmethod
    async def execute(
        self,
        *,
        workflow: Workflow,
        context: TaskContext,
    ) -> RuntimeReport:
        """
        Execute a workflow.

        Args:
            workflow:
                Validated executable workflow.

            context:
                Runtime task context.

        Returns:
            Runtime execution report.
        """

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return runtime diagnostics.
        """

        return {
            "runtime": self.__class__.__name__,
        }