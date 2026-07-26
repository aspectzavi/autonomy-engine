"""
Rule-based agent planner.

Provides the default implementation of AgentPlanner.

The planner performs deterministic planning by translating a high-level
goal into an execution plan. Workflow construction is delegated to the
planning subsystem's PlanCompiler.
"""

from __future__ import annotations

from backend.core.agents.goal import Goal
from backend.core.agents.planner import AgentPlanner
from backend.core.planning.execution_plan import ExecutionPlan
from backend.core.planning.plan_step import PlanStep


class RuleBasedAgentPlanner(AgentPlanner):
    """
    Default rule-based planner.
    """

    async def plan(
        self,
        goal: Goal,
    ) -> ExecutionPlan:
        """
        Produce an execution plan for a goal.
        """

        #
        # Future implementations will:
        #
        # - analyze the goal
        # - invoke the reasoning subsystem
        # - decompose into subtasks
        # - assign capabilities
        # - determine dependencies
        #

        return ExecutionPlan(
            name=goal.description,
            description=goal.description,
            steps=(
                PlanStep(
                    id="goal",
                    name=goal.description,
                    description=goal.description,
                    capability="goal.execute",
                ),
            ),
        )