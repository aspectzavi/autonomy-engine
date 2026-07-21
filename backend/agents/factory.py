"""
Agent factory.

Creates and registers concrete autonomous agents.
"""

from __future__ import annotations

from backend.app.container.container import Container
from backend.core.agents.agent import Agent
from backend.core.agents.registry import AgentRegistry
from backend.agents.planning.planning_agent import PlanningAgent

class AgentFactory:
    """
    Factory for constructing autonomous agents.

    The factory owns the composition of concrete agent
    implementations but does not execute them.
    """

    def __init__(
        self,
        *,
        container: Container,
        registry: AgentRegistry,
    ) -> None:
        self._container = container
        self._registry = registry

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def container(self) -> Container:
        """
        Dependency injection container.
        """
        return self._container

    @property
    def registry(self) -> AgentRegistry:
        """
        Agent registry.
        """
        return self._registry

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        agent: Agent,
    ) -> Agent:
        """
        Register an agent instance.
        """
        self.registry.register(agent)

        return agent

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def build(self) -> None:
        """
        Build and register the default agent set.

        Concrete agents are added here as they become available.
        """

        # Example (future):
        #
        # self.register(
        #     BrowserAgent(...)
        # )
        #
        # self.register(
        #     CodingAgent(...)
        # )
        #
        # self.register(
        #     DesktopAgent(...)
        # )
        #
        self.register(
            PlanningAgent()
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return factory diagnostics.
        """
        return {
            "registered_agents": len(
                self.registry,
            ),
            "agents": [
                agent.name
                for agent in self.registry
            ],
        }