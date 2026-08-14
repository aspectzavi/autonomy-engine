"""
Agent manager tests.
"""

from __future__ import annotations

from backend.core.agents.manager import AgentManager
from backend.core.agents.registry import AgentRegistry


def test_manager_uses_the_injected_registry_even_when_empty() -> None:
    """
    Regression test: AgentManager must keep an injected AgentRegistry
    even when it is empty.

    AgentRegistry defines __len__, so `registry or AgentRegistry()`
    is a real footgun -- an empty-but-valid injected registry is
    falsy and would be silently replaced by a new, disconnected one.
    The check must be `is None`.
    """

    registry = AgentRegistry()
    assert len(registry) == 0

    manager = AgentManager(registry=registry)

    assert manager.registry is registry


def test_manager_defaults_to_a_new_registry_when_none_given() -> None:
    manager = AgentManager()

    assert isinstance(manager.registry, AgentRegistry)
    assert len(manager.registry) == 0
