"""
Workflow service.

Runtime-managed service responsible for coordinating workflow
execution throughout the autonomy engine.

The service is intentionally thin. It delegates orchestration to the
WorkflowRuntime, which coordinates scheduling and execution.
"""

from __future__ import annotations

from backend.core.kernel.metadata import ServiceMetadata
from backend.core.kernel.service import KernelService
from backend.core.tasks.context import TaskContext
from backend.core.workflows.default_workflow_runtime import (
    DefaultWorkflowRuntime,
)
from backend.core.workflows.rule_based_workflow_executor import (
    RuleBasedWorkflowExecutor,
)
from backend.core.workflows.rule_based_workflow_scheduler import (
    RuleBasedWorkflowScheduler,
)
from backend.core.workflows.runtime_report import (
    RuntimeReport,
)
from backend.core.workflows.workflow import Workflow
from backend.core.workflows.workflow_runtime import (
    WorkflowRuntime,
)


class WorkflowService(KernelService):
    """
    Runtime service for workflow execution.
    """

    def __init__(
        self,
        *,
        workflow_runtime: WorkflowRuntime | None = None,
    ) -> None:
        super().__init__(
            metadata=ServiceMetadata(
                name="workflow-service",
                version="1.0.0",
                description=(
                    "Coordinates execution of autonomous workflows."
                ),
            ),
        )

        self._workflow_runtime = (
            workflow_runtime
            or DefaultWorkflowRuntime(
                scheduler=RuleBasedWorkflowScheduler(),
                executor=RuleBasedWorkflowExecutor(),
            )
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def workflow_runtime(
        self,
    ) -> WorkflowRuntime:
        """
        Workflow runtime.
        """

        return self._workflow_runtime

    # ------------------------------------------------------------------
    # Lifecycle Hooks
    # ------------------------------------------------------------------

    async def on_start(
        self,
    ) -> None:
        """
        Start workflow infrastructure.
        """

    async def on_stop(
        self,
    ) -> None:
        """
        Stop workflow infrastructure.
        """

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def execute(
        self,
        workflow: Workflow,
        context: TaskContext,
    ) -> RuntimeReport:
        """
        Execute a workflow.
        """

        return await self.workflow_runtime.execute(
            workflow=workflow,
            context=context,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return workflow service diagnostics.
        """

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "workflow_runtime": (
                    self.workflow_runtime.diagnostics()
                ),
            }
        )

        return diagnostics