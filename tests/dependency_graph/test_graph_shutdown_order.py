"""
DependencyGraph shutdown_order() tests.
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
    Simple service used for shutdown ordering tests.
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
    Build a dependency graph with a simple dependency chain.

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


def test_graph_shutdown_order() -> None:
    """
    shutdown_order() should be the reverse
    of startup_order().
    """

    graph = build_graph()

    assert graph.shutdown_order() == (
        "workflow",
        "agent",
        "cache",
        "database",
    )


def test_graph_shutdown_is_reverse_of_startup() -> None:
    """
    shutdown_order() should always equal
    reversed(startup_order()).
    """

    graph = build_graph()

    assert graph.shutdown_order() == tuple(
        reversed(
            graph.startup_order(),
        )
    )