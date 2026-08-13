"""
DependencyGraph startup_order() tests.
"""

from __future__ import annotations

from backend.core.kernel.dependency_graph import DependencyGraph
from backend.core.kernel.metadata import ServiceMetadata
from backend.core.kernel.registry import (
    ServiceRegistration,
    ServiceRegistry,
)
from backend.core.kernel.service import KernelService


class DummyService(KernelService):
    """
    Simple service used for startup ordering tests.
    """

    def __init__(
        self,
        name: str,
    ) -> None:
        super().__init__(
            ServiceMetadata(
                name=name,
                version="1.0.0",
            ),
        )


def build_graph() -> DependencyGraph:
    """
    Build a dependency graph with a realistic dependency chain.

        database
            │
            ▼
          cache
            │
            ▼
          agent
            │
            ▼
        workflow
    """

    registry = ServiceRegistry()

    for name in (
        "database",
        "cache",
        "agent",
        "workflow",
    ):
        service = DummyService(name)

        registry.register(
            ServiceRegistration(
                metadata=service.metadata,
                service=service,
            )
        )

    graph = DependencyGraph(registry)

    graph.add(
        "cache",
        "database",
    )

    graph.add(
        "agent",
        "cache",
    )

    graph.add(
        "workflow",
        "agent",
    )

    return graph


def test_graph_startup_order() -> None:
    """
    startup_order() should return a valid topological
    ordering where every dependency appears before the
    service that depends on it.
    """

    graph = build_graph()

    assert graph.startup_order() == (
        "database",
        "cache",
        "agent",
        "workflow",
    )


def test_graph_startup_order_is_deterministic() -> None:
    """
    Multiple calls should always produce the same order.
    """

    graph = build_graph()

    first = graph.startup_order()
    second = graph.startup_order()

    assert first == second