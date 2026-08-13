"""
Planning agent.

Concrete autonomous agent responsible for high-level planning.

The planning agent coordinates the translation of user goals into
executable workflows using an AgentPlanner implementation.

Unlike the generic Agent base class, the PlanningAgent owns the
ReasoningEngine. Future versions execute the reasoning stage before
planning while keeping the planner focused solely on plan generation.
"""

from __future__ import annotations

from backend.agents.planning.planner import (
    RuleBasedAgentPlanner,
)
from backend.core.agents.agent import Agent
from backend.core.memory.experience_recorder import (
    ExperienceRecorder,
)
from backend.core.planning.plan_compiler import (
    PlanCompiler,
)
from backend.core.planning.plan_optimizer import (
    PlanOptimizer,
)
from backend.core.planning.rule_based_plan_optimizer import (
    RuleBasedPlanOptimizer,
)
from backend.core.reasoning.reasoning_engine import (
    ReasoningEngine,
)
from backend.core.reasoning.reasoning_pipeline import (
    ReasoningPipeline,
)
from backend.core.reasoning.reasoning_result import (
    ReasoningResult,
)
from backend.core.services.workflow_service import (
    WorkflowService,
)
from backend.core.agents.context import AgentContext
from backend.core.agents.goal import Goal


class PlanningAgent(Agent):
    """
    Default planning agent.
    """

    def __init__(
        self,
        *,
        compiler: PlanCompiler,
        workflow_service: WorkflowService,
        reasoning_engine: ReasoningEngine,
        experience_recorder: ExperienceRecorder,
        optimizer: PlanOptimizer | None = None,
    ) -> None:
        self._reasoning_engine = reasoning_engine

        self._reasoning_pipeline = ReasoningPipeline(
            engine=reasoning_engine,
        )

        planner = RuleBasedAgentPlanner(
            reasoning_engine=reasoning_engine,
        )

        super().__init__(
            name="planning",
            planner=planner,
            optimizer=optimizer
            or RuleBasedPlanOptimizer(),
            compiler=compiler,
            workflow_service=workflow_service,
            experience_recorder=experience_recorder,
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def reasoning_engine(
        self,
    ) -> ReasoningEngine:
        """
        Reasoning engine owned by the planning agent.
        """

        return self._reasoning_engine

    @property
    def description(
        self,
    ) -> str:
        """
        Human-readable agent description.
        """

        return (
            "Plans and coordinates execution workflows "
            "for autonomous goals."
        )

    # ------------------------------------------------------------------
    # Reasoning
    # ------------------------------------------------------------------

    async def reason(
        self,
        goal: Goal,
        context: AgentContext,
    ) -> ReasoningResult:
        """
        Execute the reasoning pipeline.
        """

        return await self._reasoning_pipeline.run(
            goal=goal,
            context=context,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return planning agent diagnostics.
        """

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "description": self.description,
                "planner": type(
                    self.planner,
                ).__name__,
                "optimizer": type(
                    self.optimizer,
                ).__name__,
                "reasoning_engine": type(
                    self.reasoning_engine,
                ).__name__,
                "reasoning_pipeline": (
                    self._reasoning_pipeline.diagnostics()
                ),
            }
        )

        return diagnostics