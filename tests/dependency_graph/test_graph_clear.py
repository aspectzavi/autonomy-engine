"""
DependencyGraph clear() tests.
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
    Simple service used for graph tests.
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
    registry = ServiceRegistry()

    for name in (
        "database",
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
    )

    graph.add(
        "workflow",
        "agent",
    )

    return graph


def test_graph_clear() -> None:
    """
    clear() should remove every dependency edge.
    """

    graph = build_graph()

    assert len(graph) == 2

    graph.clear()

    assert len(graph) == 0

    #
    # All relationships should disappear.
    #
    assert graph.dependencies("agent") == ()
    assert graph.dependencies("workflow") == ()

    assert graph.dependents("database") == ()
    assert graph.dependents("agent") == ()

    #
    # Startup/shutdown order should still include
    # every registered service.
    #
    assert set(graph.startup_order()) == {
        "database",
        "agent",
        "workflow",
    }