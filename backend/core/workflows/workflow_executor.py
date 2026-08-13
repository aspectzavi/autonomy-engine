"""
Workflow executor.

Defines the interface responsible for executing a scheduling plan.

The executor consumes a SchedulingPlan and produces an ExecutionResult.

Responsibilities:

- execute scheduling batches
- preserve scheduling order
- coordinate task execution
- aggregate execution results

Concrete implementations may support:

- sequential execution
- parallel execution
- distributed execution
- adaptive scheduling
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from backend.core.tasks.context import (
    TaskContext,
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


class WorkflowExecutor(ABC):
    """
    Base workflow executor.
    """

    @abstractmethod
    async def execute(
        self,
        *,
        workflow: Workflow,
        schedule: SchedulingPlan,
        context: TaskContext,
    ) -> ExecutionResult:
        """
        Execute a scheduled workflow.

        Args:
            workflow:
                Workflow produced by the graph compiler.

            schedule:
                Scheduling plan produced by the scheduler.

            context:
                Runtime task context.

        Returns:
            Immutable execution result.
        """

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return executor diagnostics.
        """

        return {
            "executor": self.__class__.__name__,
        }