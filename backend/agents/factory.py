"""
Agent factory.

Creates and registers the framework's built-in autonomous agents.
"""

from __future__ import annotations

from backend.agents.planning.planning_agent import PlanningAgent
from backend.app.container.container import Container
from backend.core.agents.agent import Agent
from backend.core.agents.registry import AgentRegistry


class AgentFactory:
    """
    Factory responsible for constructing and registering
    the framework's built-in autonomous agents.
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
    def container(
        self,
    ) -> Container:
        """
        Dependency injection container.
        """
        return self._container

    @property
    def registry(
        self,
    ) -> AgentRegistry:
        """
        Agent registry.
        """
        return self._registry

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def create_all(
        self,
    ) -> tuple[Agent, ...]:
        """
        Create all built-in agents.

        Agents are resolved through the dependency injection container
        so their dependencies can be injected automatically.
        """
        return (
            self.container.resolve(
                PlanningAgent,
            ),
        )

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
        self.registry.register(
            agent,
        )

        return agent

    def register_all(
        self,
    ) -> None:
        """
        Register all built-in agents.

        Registration is idempotent. Agents that are already registered
        are skipped.
        """
        for agent in self.create_all():
            if not self.registry.contains(
                agent.name,
            ):
                self.register(
                    agent,
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
        agents = self.create_all()

        return {
            "agent_count": len(
                agents,
            ),
            "agents": [
                agent.name
                for agent in agents
            ],
        }