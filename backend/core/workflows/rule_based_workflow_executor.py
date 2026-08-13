"""
Rule-based workflow executor.

Default implementation of WorkflowExecutor.

The executor walks the SchedulingPlan in order and executes every task
contained within each SchedulingGroup.

Tasks within a single SchedulingGroup carry no dependency on one
another (the scheduler guarantees this), so they are executed
concurrently via asyncio.gather. Groups themselves are still executed
in order, since a later group may depend on an earlier one.
"""

from __future__ import annotations

import asyncio

from backend.core.tasks.context import (
    TaskContext,
)
from backend.core.tasks.result import (
    TaskResult,
)
from backend.core.workflows.execution_batch import (
    ExecutionBatch,
)
from backend.core.workflows.execution_result import (
    ExecutionResult,
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


class RuleBasedWorkflowExecutor(
    WorkflowExecutor,
):
    """
    Default deterministic workflow executor.
    """

    async def execute(
        self,
        *,
        workflow: Workflow,
        schedule: SchedulingPlan,
        context: TaskContext,
    ) -> ExecutionResult:
        """
        Execute the supplied scheduling plan.
        """

        completed_batches = 0
        completed_tasks = 0
        failed_tasks = 0

        #
        # Build a lookup table for workflow nodes.
        #
        nodes = {
            node.id: node
            for node in workflow.graph.nodes
        }

        #
        # Execute scheduling groups in order. Groups may depend on
        # earlier groups, so groups themselves run sequentially.
        #
        for order, group in enumerate(
            schedule.groups,
        ):
            batch = ExecutionBatch(
                group=group,
                order=order,
            )

            #
            # Tasks within a batch have no dependency on one another
            # (guaranteed by the scheduler), so they run concurrently.
            #
            results = await asyncio.gather(
                *(
                    nodes[task_id].task.execute(
                        context,
                    )
                    for task_id in batch.task_ids
                ),
                return_exceptions=True,
            )

            for outcome in results:
                if isinstance(
                    outcome,
                    BaseException,
                ):
                    failed_tasks += 1
                    continue

                result: TaskResult = outcome

                if result.success:
                    completed_tasks += 1
                else:
                    failed_tasks += 1

            completed_batches += 1

        return ExecutionResult(
            success=failed_tasks == 0,
            completed_batches=completed_batches,
            completed_tasks=completed_tasks,
            failed_tasks=failed_tasks,
            metadata={
                "executor": (
                    self.__class__.__name__
                ),
                "strategy": (
                    "batch_parallel"
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
        Return executor diagnostics.
        """

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "strategy": "rule-based",
                "parallel_execution": True,
            }
        )

        return diagnostics