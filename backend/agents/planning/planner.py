"""
Rule-based agent planner.

Provides the default implementation of AgentPlanner.

The planner performs deterministic planning by translating a high-level
goal into an execution plan.

Planning is memory-aware but remains deterministic. Retrieved execution
memories are made available for future reasoning without coupling the
planner to the memory subsystem.
"""

from __future__ import annotations

from backend.core.agents.context import AgentContext
from backend.core.agents.goal import Goal
from backend.core.agents.planner import AgentPlanner
from backend.core.planning.execution_plan import ExecutionPlan
from backend.core.planning.memory_analyzer import (
    PlanningMemoryAnalyzer,
)
from backend.core.planning.plan_step import PlanStep


class RuleBasedAgentPlanner(AgentPlanner):
    """
    Default rule-based planner.
    """

    def __init__(
        self,
        *,
        analyzer: PlanningMemoryAnalyzer | None = None,
    ) -> None:
        self._analyzer = (
            analyzer
            or PlanningMemoryAnalyzer()
        )

    @property
    def analyzer(
        self,
    ) -> PlanningMemoryAnalyzer:
        """
        Planning memory analyzer.
        """
        return self._analyzer

    async def plan(
        self,
        goal: Goal,
        context: AgentContext,
    ) -> ExecutionPlan:
        """
        Produce an execution plan for a goal.
        """

        planning_insights = self.analyzer.analyze(
            context.memory,
        )

        #
        # Future versions will use planning_insights to
        # influence decomposition and task ordering.
        #
        _ = planning_insights

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