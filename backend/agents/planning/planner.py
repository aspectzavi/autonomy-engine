"""
Rule-based agent planner.

Provides the default implementation of AgentPlanner.

The planner performs deterministic planning by translating a high-level
goal into an execution plan.

Planning is memory-aware and reasoning-aware.

The ReasoningEngine is responsible for deciding *what* should be done,
while the planner is responsible for determining *how* to execute it.
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
from backend.core.reasoning.reasoning_engine import (
    ReasoningEngine,
)
from backend.core.reasoning.reasoning_result import (
    ReasoningResult,
)


class RuleBasedAgentPlanner(AgentPlanner):
    """
    Default rule-based planner.
    """

    def __init__(
        self,
        *,
        reasoning_engine: ReasoningEngine,
        analyzer: PlanningMemoryAnalyzer | None = None,
    ) -> None:
        self._reasoning_engine = reasoning_engine
        self._analyzer = (
            analyzer
            or PlanningMemoryAnalyzer()
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def reasoning_engine(
        self,
    ) -> ReasoningEngine:
        """
        Reasoning engine used before planning.
        """

        return self._reasoning_engine

    @property
    def analyzer(
        self,
    ) -> PlanningMemoryAnalyzer:
        """
        Planning memory analyzer.
        """

        return self._analyzer

    # ------------------------------------------------------------------
    # Planning
    # ------------------------------------------------------------------

    async def plan(
        self,
        goal: Goal,
        context: AgentContext,
        reasoning: ReasoningResult,
    ) -> ExecutionPlan:
        """
        Produce an execution plan for a goal.

        The reasoning engine will be invoked in a subsequent
        implementation step.
        """

        planning_insights = self.analyzer.analyze(
            context.memory,
        )

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
            metadata={
                "reasoning": {
                    "strategy": reasoning.strategy,
                    "decision": reasoning.decision.outcome,
                    "confidence": reasoning.confidence,
                },
            },
        )