"""
DependencyGraph dependents() tests.
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
    Build a dependency graph with several relationships.
    """

    registry = ServiceRegistry()

    for name in (
        "database",
        "cache",
        "agent",
        "workflow",
        "scheduler",
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

    graph.add(
        "scheduler",
        "agent",
    )

    return graph


def test_graph_dependents() -> None:
    """
    dependents() should return every service that
    directly depends on the requested service.
    """

    graph = build_graph()

    assert graph.dependents("database") == (
        "agent",
    )

    assert graph.dependents("cache") == (
        "agent",
    )

    assert graph.dependents("agent") == (
        "scheduler",
        "workflow",
    )


def test_graph_dependents_empty() -> None:
    """
    Services without dependents should return
    an empty tuple.
    """

    graph = build_graph()

    assert graph.dependents("workflow") == ()
    assert graph.dependents("scheduler") == ()