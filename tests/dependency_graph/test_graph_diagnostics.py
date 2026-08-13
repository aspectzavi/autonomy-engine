"""
DependencyGraph diagnostics() tests.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

from backend.core.kernel.dependency_graph import DependencyGraph
from backend.core.kernel.metadata import ServiceMetadata
from backend.core.kernel.registry import (
    ServiceRegistration,
    ServiceRegistry,
)
from backend.core.kernel.service import KernelService


class DummyService(KernelService):
    """
    Simple service used for diagnostics tests.
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


def test_graph_diagnostics() -> None:
    """
    diagnostics() should accurately describe the graph.
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

    graph = DependencyGraph(registry)

    graph.add(
        "agent",
        "database",
    )

    graph.add(
        "workflow",
        "agent",
    )

    diagnostics = cast(
        Mapping[str, Any],
        graph.diagnostics(),
    )

    assert diagnostics["services"] == 3
    assert diagnostics["edges"] == 2

    assert diagnostics["startup_order"] == (
        "database",
        "agent",
        "workflow",
    )

    assert diagnostics["shutdown_order"] == (
        "workflow",
        "agent",
        "database",
    )