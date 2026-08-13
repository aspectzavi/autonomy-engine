"""
Rule-based agent planner.

Provides the default implementation of AgentPlanner.

The planner coordinates planning by combining runtime analysis with a
planning policy.

Reasoning determines *what* should be done.

The planning policy determines *how* the execution plan should be
constructed.
"""

from __future__ import annotations

from backend.core.agents.context import AgentContext
from backend.core.agents.goal import Goal
from backend.core.agents.planner import AgentPlanner
from backend.core.planning.execution_plan import ExecutionPlan
from backend.core.planning.memory_analyzer import (
    PlanningMemoryAnalyzer,
)
from backend.core.planning.planning_policy import (
    PlanningPolicy,
)
from backend.core.planning.rule_based_planning_policy import (
    RuleBasedPlanningPolicy,
)
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
        policy: PlanningPolicy | None = None,
    ) -> None:
        self._reasoning_engine = reasoning_engine

        self._analyzer = (
            analyzer
            or PlanningMemoryAnalyzer()
        )

        self._policy = (
            policy
            or RuleBasedPlanningPolicy()
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

    @property
    def policy(
        self,
    ) -> PlanningPolicy:
        """
        Planning policy responsible for producing execution plans.
        """

        return self._policy

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
        Produce an execution plan.

        The planner performs runtime analysis before delegating plan
        construction to the configured planning policy.
        """

        planning_insights = self.analyzer.analyze(
            context.memory,
        )

        return await self.policy.build_plan(
            goal=goal,
            context=context,
            reasoning=reasoning,
            insights=planning_insights,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return planner diagnostics.
        """

        return {
            "reasoning_engine": (
                type(
                    self.reasoning_engine,
                ).__name__
            ),
            "analyzer": (
                type(
                    self.analyzer,
                ).__name__
            ),
            "policy": (
                type(
                    self.policy,
                ).__name__
            ),
        }