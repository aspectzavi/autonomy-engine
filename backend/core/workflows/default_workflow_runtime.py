"""
Default workflow runtime.

Coordinates workflow scheduling and execution.

The runtime is responsible for orchestrating the workflow lifecycle but
delegates scheduling and execution to dedicated components.
"""

from __future__ import annotations

from backend.core.tasks.context import (
    TaskContext,
)
from backend.core.workflows.execution_result import (
    ExecutionResult,
)
from backend.core.workflows.runtime_report import (
    RuntimeReport,
)
from backend.core.workflows.scheduling_plan import (
    SchedulingPlan,
)
from backend.core.workflows.workflow import (
    Workflow,
)
from backend.core.workflows.workflow_executor import (
    WorkflowExecutor,
)
from backend.core.workflows.workflow_runtime import (
    WorkflowRuntime,
)
from backend.core.workflows.workflow_scheduler import (
    WorkflowScheduler,
)


class DefaultWorkflowRuntime(
    WorkflowRuntime,
):
    """
    Default implementation of the workflow runtime.
    """

    def __init__(
        self,
        *,
        scheduler: WorkflowScheduler,
        executor: WorkflowExecutor,
    ) -> None:
        self._scheduler = scheduler
        self._executor = executor

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def scheduler(
        self,
    ) -> WorkflowScheduler:
        """
        Workflow scheduler.
        """

        return self._scheduler

    @property
    def executor(
        self,
    ) -> WorkflowExecutor:
        """
        Workflow executor.
        """

        return self._executor

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def execute(
        self,
        *,
        workflow: Workflow,
        context: TaskContext,
    ) -> RuntimeReport:
        """
        Execute a workflow.
        """

        #
        # Ensure workflow is ready.
        #
        workflow.validate()

        #
        # Produce scheduling plan.
        #
        schedule: SchedulingPlan = (
            await self.scheduler.schedule(
                workflow,
            )
        )

        #
        # Execute schedule.
        #
        execution: ExecutionResult = (
            await self.executor.execute(
                workflow=workflow,
                schedule=schedule,
                context=context,
            )
        )

        #
        # Produce immutable runtime report.
        #
        return RuntimeReport(
            schedule=schedule,
            execution=execution,
            metadata={
                "runtime": (
                    self.__class__.__name__
                ),
            },
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return runtime diagnostics.
        """

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "scheduler": (
                    type(
                        self.scheduler,
                    ).__name__
                ),
                "executor": (
                    type(
                        self.executor,
                    ).__name__
                ),
            }
        )

        return diagnostics