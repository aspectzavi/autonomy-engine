"""
Agent manager.

Coordinates autonomous agents through the agent registry.
"""

from __future__ import annotations

from backend.core.agents.goal import Goal
from backend.core.agents.registry import AgentRegistry
from backend.core.agents.result import AgentResult
from backend.core.tasks.context import TaskContext
from backend.core.agents.agent import Agent

class AgentManager:
    """
    Coordinates registered autonomous agents.

    The manager is responsible for dispatching goals to agents and
    exposing registry-level diagnostics. It does not implement planning
    or execution logic itself.
    """

    def __init__(
        self,
        registry: AgentRegistry | None = None,
    ) -> None:
        self._registry = registry or AgentRegistry()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def registry(self) -> AgentRegistry:
        """
        Return the managed agent registry.
        """
        return self._registry

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        agent: Agent,
    ) -> None:
        """
        Register an agent.
        """
        self.registry.register(agent)

    def unregister(self, name: str) -> None:
        """
        Unregister an agent.
        """
        self.registry.unregister(name)

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get(
        self,
        name: str,
    ) -> Agent:
        """
        Return a registered agent.
        """
        return self.registry.get(name)

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def execute(
        self,
        *,
        agent: str,
        goal: Goal,
        task_context: TaskContext,
    ) -> AgentResult:
        """
        Execute a goal using the specified agent.
        """
        selected = self.registry.get(agent)

        return await selected.execute(
            goal=goal,
            task_context=task_context,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(self) -> dict[str, object]:
        """
        Return manager diagnostics.
        """
        return {
            "registered_agents": len(self.registry),
            "registry": self.registry.diagnostics(),
        }