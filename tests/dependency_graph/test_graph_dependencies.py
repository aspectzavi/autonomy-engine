"""
DependencyGraph dependencies() tests.
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
    Simple service used for dependency graph tests.
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
    Build a dependency graph with several services.
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
        "agent",
        "database",
        "cache",
    )

    graph.add(
        "workflow",
        "agent",
    )

    return graph


def test_graph_dependencies() -> None:
    """
    dependencies() should return all direct dependencies
    in deterministic sorted order.
    """

    graph = build_graph()

    assert graph.dependencies("agent") == (
        "cache",
        "database",
    )

    assert graph.dependencies("workflow") == (
        "agent",
    )


def test_graph_dependencies_empty() -> None:
    """
    Services without dependencies should return
    an empty tuple.
    """

    graph = build_graph()

    assert graph.dependencies("database") == ()
    assert graph.dependencies("cache") == ()