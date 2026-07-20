"""
Simple workflow planner.
"""

from __future__ import annotations

from backend.core.workflows.planner import WorkflowPlanner
from backend.core.workflows.workflow import Workflow


class SimpleWorkflowPlanner(WorkflowPlanner):
    """
    Minimal planner that creates an empty workflow.
    """

    async def plan(
        self,
        goal: str,
    ) -> Workflow:
        return Workflow(name=goal)