"""
Agent factory bootstrap.

Creates and initializes the framework's built-in agent factory.
"""

from __future__ import annotations

from backend.agents.factory import AgentFactory
from backend.app.container.container import Container
from backend.core.agents.manager import AgentManager
from backend.core.agents.registry import AgentRegistry


def create_agent_factory(
    container: Container,
) -> AgentFactory:
    """
    Create and initialize the built-in agent factory.
    """

    registry = container.resolve(
        AgentRegistry,
    )

    # Ensure the manager is constructed by the container.
    container.resolve(
        AgentManager,
    )

    factory = AgentFactory(
        container=container,
        registry=registry,
    )

    factory.register_all()

    return factory