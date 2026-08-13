"""
Workflow resilience.

Defines the interface responsible for applying resilience strategies
during workflow execution.

A WorkflowResilience implementation coordinates:

- retry policies
- failure classification
- timeout handling
- cancellation handling

to execute a workflow reliably.

Concrete implementations may additionally support:

- circuit breakers
- adaptive retry
- distributed recovery
- checkpoint restoration
- compensation workflows
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from backend.core.tasks.context import TaskContext
from backend.core.workflows.execution_result import (
    ExecutionResult,
)
from backend.core.workflows.resilience_report import (
    ResilienceReport,
)
from backend.core.workflows.workflow import (
    Workflow,
)
from backend.core.workflows.scheduling_plan import SchedulingPlan

class WorkflowResilience(ABC):
    """
    Base interface for workflow resilience.
    """

    @abstractmethod
    async def execute(
        self,
        *,
        workflow: Workflow,
        schedule: SchedulingPlan,
        context: TaskContext,
    ) -> tuple[
        ExecutionResult,
        ResilienceReport,
    ]:
        """
        Execute a workflow while applying resilience strategies.

        Returns:
            Tuple consisting of:

            - workflow execution result
            - resilience report
        """

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return resilience diagnostics.
        """

        return {
            "resilience": self.__class__.__name__,
        }