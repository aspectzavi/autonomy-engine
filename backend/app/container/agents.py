"""
Agent dependency registration.

Registers agent infrastructure into the dependency injection container.
"""

from __future__ import annotations

from backend.app.container.container import Container
from backend.core.agents.manager import AgentManager
from backend.core.agents.registry import AgentRegistry


def register_agents(
    container: Container,
) -> None:
    """
    Register agent infrastructure.

    Concrete agents are registered separately.
    """

    if not container.contains(
        AgentRegistry,
    ):
        container.register_singleton(
            AgentRegistry,
        )

    if not container.contains(
        AgentManager,
    ):
        container.register_singleton(
            AgentManager,
        )