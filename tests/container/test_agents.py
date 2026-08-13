"""
Agent registration tests.
"""

from __future__ import annotations

from backend.agents.planning.planning_agent import (
    PlanningAgent,
)
from backend.app.container.agents import (
    register_agents,
)
from backend.app.container.container import Container
from backend.core.agents.manager import AgentManager
from backend.core.agents.registry import AgentRegistry


def test_register_agents() -> None:
    """
    register_agents() should register the agent
    infrastructure exactly once.
    """

    container = Container()

    register_agents(
        container,
    )

    #
    # Core agent infrastructure.
    #
    assert container.contains(
        AgentRegistry,
    )

    assert container.contains(
        AgentManager,
    )

    #
    # Built-in planning agent.
    #
    assert container.contains(
        PlanningAgent,
    )

    #
    # Calling again should be idempotent.
    #
    registrations = len(
        container,
    )

    register_agents(
        container,
    )

    assert len(container) == registrations

    #
    # Resolve services.
    #
    registry = container.resolve(
        AgentRegistry,
    )

    manager = container.resolve(
        AgentManager,
    )

    planning = container.resolve(
        PlanningAgent,
    )

    assert isinstance(
        registry,
        AgentRegistry,
    )

    assert isinstance(
        manager,
        AgentManager,
    )

    assert isinstance(
        planning,
        PlanningAgent,
    )

    #
    # AgentRegistry and AgentManager are singletons.
    #
    assert (
        container.resolve(
            AgentRegistry,
        )
        is registry
    )

    assert (
        container.resolve(
            AgentManager,
        )
        is manager
    )

    #
    # PlanningAgent is transient.
    #
    assert (
        container.resolve(
            PlanningAgent,
        )
        is not planning
    )