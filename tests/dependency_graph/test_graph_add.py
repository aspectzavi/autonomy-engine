"""
DependencyGraph add() tests.
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
    Create a registry populated with three services.
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


def test_graph_add() -> None:
    """
    Dependencies should be recorded correctly.
    """

    registry = build_registry()

    graph = DependencyGraph(registry)

    graph.add(
        "workflow",
        "database",
        "agent",
    )

    assert graph.dependencies("workflow") == (
        "agent",
        "database",
    )

    assert graph.dependents("database") == (
        "workflow",
    )

    assert graph.dependents("agent") == (
        "workflow",
    )


def test_graph_add_unknown_service() -> None:
    """
    Adding an unknown service should fail.
    """

    registry = build_registry()

    graph = DependencyGraph(registry)

    with pytest.raises(
        RegistryError,
        match="Unknown service",
    ):
        graph.add(
            "unknown",
            "database",
        )


def test_graph_add_unknown_dependency() -> None:
    """
    Adding an unknown dependency should fail.
    """

    registry = build_registry()

    graph = DependencyGraph(registry)

    with pytest.raises(
        RegistryError,
        match="Unknown dependency",
    ):
        graph.add(
            "workflow",
            "missing-service",
        )