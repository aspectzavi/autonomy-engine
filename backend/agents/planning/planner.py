"""
Rule-based agent planner.

Provides the default implementation of AgentPlanner.

The planner performs simple deterministic planning by translating a
high-level goal into an executable workflow. More sophisticated
implementations (LLM, ReAct, Tree-of-Thought, etc.) can replace this
planner without affecting the rest of the system.
"""

from __future__ import annotations

from backend.core.agents.goal import Goal
from backend.core.agents.planner import AgentPlanner
from backend.core.workflows.workflow import Workflow


class RuleBasedAgentPlanner(AgentPlanner):
    """
    Default rule-based planner.

    This planner creates an empty workflow whose structure will be
    populated by future planning strategies.
    """

    async def plan(
        self,
        goal: Goal,
    ) -> Workflow:
        """
        Create an executable workflow for a goal.
        """

        workflow = Workflow(
            name=goal.description,
        )

        # Future implementations will:
        #
        # - analyze the goal
        # - decompose into subtasks
        # - create workflow nodes
        # - establish dependencies
        # - validate the workflow
        #
        # For now we simply return the workflow shell.

        return workflow