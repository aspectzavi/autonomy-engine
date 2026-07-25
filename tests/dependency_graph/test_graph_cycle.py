"""
DependencyGraph cycle detection tests.
"""

from __future__ import annotations

import pytest

from backend.core.kernel.dependency_graph import DependencyGraph
from backend.core.kernel.exceptions import RegistryError
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


def build_registry() -> ServiceRegistry:
    """
    Create a registry with three services.
    """

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

    return registry


def test_graph_cycle_detection() -> None:
    """
    Circular dependencies should be rejected.
    """

    registry = build_registry()

    graph = DependencyGraph(registry)

    #
    # database <- workflow
    # workflow <- agent
    # agent <- database
    #

    graph.add(
        "agent",
        "database",
    )

    graph.add(
        "workflow",
        "agent",
    )

    graph.add(
        "database",
        "workflow",
    )

    with pytest.raises(
        RegistryError,
        match="Circular dependency detected",
    ):
        graph.validate()


def test_graph_startup_order_cycle() -> None:
    """
    startup_order() should also detect cycles.
    """

    registry = build_registry()

    graph = DependencyGraph(registry)

    graph.add(
        "agent",
        "database",
    )

    graph.add(
        "workflow",
        "agent",
    )

    graph.add(
        "database",
        "workflow",
    )

    with pytest.raises(
        RegistryError,
        match="Circular dependency detected",
    ):
        graph.startup_order()