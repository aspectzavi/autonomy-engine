"""
ServiceRegistry diagnostics tests.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

from backend.core.kernel.metadata import ServiceMetadata
from backend.core.kernel.registry import (
    ServiceRegistration,
    ServiceRegistry,
)
from backend.core.kernel.service import KernelService


class DatabaseService(KernelService):
    """
    Simple database service.
    """

    def __init__(self) -> None:
        super().__init__(
            ServiceMetadata(
                name="database",
                version="1.0.0",
            ),
        )


class ApiService(KernelService):
    """
    Simple API service.
    """

    def __init__(self) -> None:
        super().__init__(
            ServiceMetadata(
                name="api",
                version="2.0.0",
            ),
        )


def test_registry_diagnostics() -> None:
    """
    Registry diagnostics should accurately describe all
    registered services.
    """

    registry = ServiceRegistry()

    database = DatabaseService()
    api = ApiService()

    registry.register(
        ServiceRegistration(
            metadata=database.metadata,
            service=database,
            tags=frozenset({"database"}),
        )
    )

    registry.register(
        ServiceRegistration(
            metadata=api.metadata,
            service=api,
            singleton=False,
            priority=10,
            tags=frozenset({"api", "http"}),
        )
    )

    diagnostics = registry.diagnostics()

    assert diagnostics["service_count"] == 2

    services = cast(
        list[Mapping[str, Any]],
        diagnostics["services"],
    )

    assert len(services) == 2

    #
    # Convert to a dictionary keyed by service name so the
    # assertions do not depend on registration order.
    #
    by_name = {
        cast(str, service["name"]): service
        for service in services
    }

    #
    # Database service.
    #
    database_diag = by_name["database"]

    assert database_diag["version"] == "1.0.0"
    assert database_diag["enabled"] is True
    assert database_diag["singleton"] is True
    assert database_diag["priority"] == 0
    assert database_diag["tags"] == ["database"]

    #
    # API service.
    #
    api_diag = by_name["api"]

    assert api_diag["version"] == "2.0.0"
    assert api_diag["enabled"] is True
    assert api_diag["singleton"] is False
    assert api_diag["priority"] == 10
    assert api_diag["tags"] == ["api", "http"]