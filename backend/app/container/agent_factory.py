"""
Agent factory registration.
"""

from __future__ import annotations

from backend.agents.factory import AgentFactory
from backend.app.container.container import Container
from backend.core.agents.registry import AgentRegistry


def create_agent_factory(
    container: Container,
) -> AgentFactory:
    """
    Create the application's agent factory.
    """

    registry = container.resolve(
        AgentRegistry,
    )

    factory = AgentFactory(
        container=container,
        registry=registry,
    )

    factory.build()

    return factory