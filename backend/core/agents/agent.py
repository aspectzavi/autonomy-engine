"""
Agent base class.

Defines the base implementation for all autonomous agents.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from backend.core.agents.context import AgentContext
from backend.core.agents.goal import Goal
from backend.core.agents.planner import AgentPlanner
from backend.core.agents.result import AgentResult
from backend.core.agents.state import AgentState
from backend.core.memory.experience_recorder import (
    ExperienceRecorder,
)
from backend.core.planning.plan_compiler import PlanCompiler
from backend.core.reasoning.reasoning_result import (
    ReasoningResult,
)
from backend.core.services.workflow_service import (
    WorkflowService,
)
from backend.core.tasks.context import TaskContext


class Agent(ABC):
    """
    Base class for autonomous agents.

    An agent coordinates reasoning, planning and execution while
    delegating workflow creation and task execution to the workflow
    subsystem.
    """

    def __init__(
        self,
        *,
        name: str,
        planner: AgentPlanner,
        compiler: PlanCompiler,
        workflow_service: WorkflowService,
        experience_recorder: ExperienceRecorder,
    ) -> None:
        self._name = name
        self._planner = planner
        self._compiler = compiler
        self._workflow_service = workflow_service
        self._experience_recorder = experience_recorder
        self._state = AgentState.IDLE

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def name(
        self,
    ) -> str:
        """
        Agent name.
        """

        return self._name

    @property
    def planner(
        self,
    ) -> AgentPlanner:
        """
        Planner used by the agent.
        """

        return self._planner

    @property
    def workflow_service(
        self,
    ) -> WorkflowService:
        """
        Runtime workflow service.
        """

        return self._workflow_service

    @property
    def experience_recorder(
        self,
    ) -> ExperienceRecorder:
        """
        Records execution experiences.
        """

        return self._experience_recorder

    @property
    def state(
        self,
    ) -> AgentState:
        """
        Current agent state.
        """

        return self._state

    @property
    def compiler(
        self,
    ) -> PlanCompiler:
        """
        Execution plan compiler.
        """

        return self._compiler

    # ------------------------------------------------------------------
    # Reasoning
    # ------------------------------------------------------------------

    @abstractmethod
    async def reason(
        self,
        goal: Goal,
        context: AgentContext,
    ) -> ReasoningResult:
        """
        Execute the agent-specific reasoning stage.
        """

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def execute(
        self,
        goal: Goal,
        task_context: TaskContext,
        context: AgentContext | None = None,
    ) -> AgentResult:
        """
        Execute a goal.
        """

        if context is None:
            raise ValueError(
                "AgentContext must be provided by the runtime.",
            )

        self._state = AgentState.PLANNING

        started_at = goal.created_at

        try:
            reasoning = await self.reason(
                goal,
                context,
            )

            plan = await self.planner.plan(
                goal=goal,
                context=context,
                reasoning=reasoning,
            )

            workflow = self.compiler.compile(
                plan,
            )

            self._state = AgentState.EXECUTING

            workflow_result = await self.workflow_service.execute(
                workflow,
                task_context,
            )

            if context.memory is not None:
                context.memory.remember(
                    self.experience_recorder.record_success(
                        goal=goal.description,
                        agent=self.name,
                    ),
                )

            self._state = AgentState.COMPLETED

            return AgentResult.ok(
                agent=self.name,
                goal=goal.description,
                workflow_result=workflow_result,
                started_at=started_at,
            )

        except Exception as exc:
            if context.memory is not None:
                context.memory.remember(
                    self.experience_recorder.record_failure(
                        goal=goal.description,
                        agent=self.name,
                        error=str(exc),
                    ),
                )

            self._state = AgentState.FAILED

            return AgentResult.failure(
                agent=self.name,
                goal=goal.description,
                error=str(exc),
                started_at=started_at,
            )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return agent diagnostics.
        """

        return {
            "name": self.name,
            "state": self.state.value,
            "planner": type(
                self.planner,
            ).__name__,
            "workflow_service": type(
                self.workflow_service,
            ).__name__,
            "compiler": type(
                self.compiler,
            ).__name__,
        }