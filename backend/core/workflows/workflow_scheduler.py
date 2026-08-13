"""
Workflow scheduler.

Defines the interface responsible for converting a validated Workflow
into an executable scheduling plan.

Schedulers determine execution ordering while respecting workflow
dependencies.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from backend.core.workflows.scheduling_plan import (
    SchedulingPlan,
)
from backend.core.workflows.workflow import (
    Workflow,
)


class WorkflowScheduler(ABC):
    """
    Base workflow scheduler.
    """

    @abstractmethod
    async def schedule(
        self,
        workflow: Workflow,
    ) -> SchedulingPlan:
        """
        Produce a scheduling plan for a workflow.
        """

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        return {
            "scheduler": self.__class__.__name__,
        }