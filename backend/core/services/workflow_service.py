"""
Workflow service.

Runtime-managed service responsible for coordinating workflow
execution throughout the autonomy engine.
"""

from __future__ import annotations

from backend.core.kernel.metadata import ServiceMetadata
from backend.core.kernel.service import KernelService
from backend.core.workflows.executor import WorkflowExecutor
from backend.core.workflows.workflow import Workflow
from backend.core.tasks.context import TaskContext
from backend.core.workflows.result import WorkflowResult


class WorkflowService(KernelService):
    """
    Runtime service for workflow execution.
    """

    def __init__(
        self,
        *,
        executor: WorkflowExecutor | None = None,
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

        self._executor = (
            executor
            or WorkflowExecutor()
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def executor(
        self,
    ) -> WorkflowExecutor:
        """
        Workflow executor.
        """
        return self._executor

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
    ) -> WorkflowResult:
        """
        Execute a workflow.
        """
        return await self.executor.execute(
            workflow,
            context,
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
                "executor": (
                    self.executor.diagnostics()
                ),
            }
        )

        return diagnostics