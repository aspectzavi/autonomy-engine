"""
Planning agent.

Concrete autonomous agent responsible for high-level planning.

The planning agent coordinates the translation of user goals into
executable workflows using an AgentPlanner implementation.
"""

from __future__ import annotations

from backend.agents.planning.planner import RuleBasedAgentPlanner
from backend.core.agents.agent import Agent
from backend.core.memory.experience_recorder import (
    ExperienceRecorder,
)
from backend.core.planning.plan_compiler import PlanCompiler
from backend.core.services.workflow_service import WorkflowService


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
        experience_recorder: ExperienceRecorder,
    ) -> None:
        super().__init__(
            name="planning",
            planner=RuleBasedAgentPlanner(),
            compiler=compiler,
            workflow_service=workflow_service,
            experience_recorder=experience_recorder,
        )

    @property
    def description(self) -> str:
        """
        Human-readable agent description.
        """
        return (
            "Plans and coordinates execution workflows "
            "for autonomous goals."
        )

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
                "planner": type(self.planner).__name__,
            }
        )

        return diagnostics