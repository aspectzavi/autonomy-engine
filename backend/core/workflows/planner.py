"""
Workflow planner.

Defines the interface for constructing executable workflows.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from backend.core.workflows.workflow import Workflow


class WorkflowPlanner(ABC):
    """
    Base class for workflow planners.

    A planner translates a high-level goal into an executable workflow.
    """

    @abstractmethod
    async def plan(
        self,
        goal: str,
    ) -> Workflow:
        """
        Create a workflow for the given goal.
        """
        raise NotImplementedError