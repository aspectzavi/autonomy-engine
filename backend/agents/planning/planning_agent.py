"""
Planning agent.

Concrete autonomous agent responsible for high-level planning.

The planning agent coordinates the translation of user goals into
executable workflows using an AgentPlanner implementation.

Unlike the generic Agent base class, the PlanningAgent owns the
ReasoningEngine and ReasoningPipeline. The reasoning pipeline executes
before planning, allowing the planner to focus solely on transforming
reasoning decisions into execution plans.
"""

from __future__ import annotations

from backend.agents.planning.planner import (
    RuleBasedAgentPlanner,
)
from backend.core.agents.agent import Agent
from backend.core.agents.context import AgentContext
from backend.core.agents.goal import Goal
from backend.core.memory.experience_recorder import (
    ExperienceRecorder,
)
from backend.core.planning.plan_compiler import (
    PlanCompiler,
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


class PlanningAgent(Agent):
    """
    Default planning agent.

    Uses the rule-based planner to translate goals into executable
    workflows.
    """

    def __init__(
        self,
        *,
        compiler: PlanCompiler,
        workflow_service: WorkflowService,
        reasoning_engine: ReasoningEngine,
        experience_recorder: ExperienceRecorder,
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
    def reasoning_pipeline(
        self,
    ) -> ReasoningPipeline:
        """
        Pipeline responsible for orchestrating reasoning.
        """

        return self._reasoning_pipeline

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
        Execute the planning reasoning pipeline.
        """

        return await self.reasoning_pipeline.run(
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
                "reasoning_engine": type(
                    self.reasoning_engine,
                ).__name__,
                "reasoning_pipeline": type(
                    self.reasoning_pipeline,
                ).__name__,
            }
        )

        return diagnostics