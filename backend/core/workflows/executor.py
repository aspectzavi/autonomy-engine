"""
Workflow executor.

Executes workflows using the existing task execution engine.
"""

from __future__ import annotations

from datetime import UTC, datetime

from backend.core.tasks.context import TaskContext
from backend.core.tasks.executor import TaskExecutor
from backend.core.tasks.result import TaskResult
from backend.core.workflows.result import WorkflowResult
from backend.core.workflows.workflow import Workflow


class WorkflowExecutor:
    """
    Executes workflows.
    """

    def __init__(
        self,
        task_executor: TaskExecutor | None = None,
    ) -> None:
        self._task_executor = task_executor or TaskExecutor()

    @property
    def task_executor(self) -> TaskExecutor:
        """
        Underlying task executor.
        """
        return self._task_executor

    async def execute(
        self,
        workflow: Workflow,
        context: TaskContext,
    ) -> WorkflowResult:
        """
        Execute a workflow.

        Tasks are executed in topological order.
        """
        started_at = datetime.now(UTC)

        workflow.validate()

        results: list[TaskResult] = []

        success = True

        for node in workflow.graph.topological_order():
            result = await self.task_executor.execute(
                node.task,
                context,
            )

            results.append(result)

            if result.failed:
                success = False
                break

        return WorkflowResult(
            workflow=workflow.name,
            success=success,
            task_results=tuple(results),
            started_at=started_at,
            finished_at=datetime.now(UTC),
        )

    def diagnostics(self) -> dict[str, object]:
        """
        Executor diagnostics.
        """
        return {
            "task_executor": self.task_executor.__class__.__name__,
        }