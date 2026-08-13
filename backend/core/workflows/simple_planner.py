"""
Simple workflow planner.
"""

from __future__ import annotations

from backend.core.workflows.planner import WorkflowPlanner
from backend.core.workflows.workflow import Workflow
from backend.core.agents.goal import Goal

class SimpleWorkflowPlanner(WorkflowPlanner):
    """
    Minimal planner that creates an empty workflow.
    """

    async def plan(
        self,
        goal: Goal,
    ) -> Workflow:
        return Workflow(
            name=goal.description,
        )