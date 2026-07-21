"""
Agent base class.

Defines the base implementation for all autonomous agents.
"""

from __future__ import annotations

from abc import ABC

from backend.core.agents.context import AgentContext
from backend.core.agents.goal import Goal
from backend.core.agents.result import AgentResult
from backend.core.agents.state import AgentState
from backend.core.workflows.executor import WorkflowExecutor
from backend.core.workflows.planner import WorkflowPlanner
from backend.core.tasks.context import TaskContext

class Agent(ABC):
    """
    Base class for autonomous agents.

    An agent coordinates planning and execution but delegates workflow
    creation and task execution to the workflow subsystem.
    """

    def __init__(
        self,
        *,
        name: str,
        planner: WorkflowPlanner,
        workflow_executor: WorkflowExecutor | None = None,
    ) -> None:
        self._name = name
        self._planner = planner
        self._workflow_executor = (
            workflow_executor
            or WorkflowExecutor()
        )
        self._state = AgentState.IDLE

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        """
        Agent name.
        """
        return self._name

    @property
    def planner(self) -> WorkflowPlanner:
        """
        Workflow planner used by the agent.
        """
        return self._planner

    @property
    def workflow_executor(self) -> WorkflowExecutor:
        """
        Workflow executor.
        """
        return self._workflow_executor

    @property
    def state(self) -> AgentState:
        """
        Current agent state.
        """
        return self._state

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
        context = context or AgentContext()

        self._state = AgentState.PLANNING

        started_at = goal.created_at

        try:
            workflow = await self.planner.plan(
                goal,
            )

            self._state = AgentState.EXECUTING

            
            workflow_result = await self.workflow_executor.execute(
                workflow,
                task_context,
            )

            self._state = AgentState.COMPLETED

            return AgentResult.ok(
                agent=self.name,
                goal=goal.description,
                workflow_result=workflow_result,
                started_at=started_at,
            )

        except Exception as exc:
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

    def diagnostics(self) -> dict[str, object]:
        """
        Return agent diagnostics.
        """
        return {
            "name": self.name,
            "state": self.state.value,
            "planner": type(self.planner).__name__,
            "workflow_executor": (
                type(self.workflow_executor).__name__
            ),
        }