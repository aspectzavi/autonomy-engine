"""
ServiceRegistry registration tests.
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


class DummyService(KernelService):
    """
    Simple service used for registry testing.
    """

    def __init__(self) -> None:
        super().__init__(
            ServiceMetadata(
                name="dummy-service",
                version="1.0.0",
            )
        )


def test_registry_register() -> None:
    """
    Registering a service should make it available through
    the registry and update diagnostics.
    """

    registry = ServiceRegistry()

    service = DummyService()

    registration = ServiceRegistration(
        metadata=service.metadata,
        service=service,
    )

    #
    # Registry should initially be empty.
    #
    assert len(registry) == 0
    assert registry.names() == ()

    #
    # Register service.
    #
    registry.register(registration)

    #
    # Registry contents.
    #
    assert len(registry) == 1

    assert "dummy-service" in registry

    assert registry.get("dummy-service") is service

    assert registry.registration(
        "dummy-service",
    ) is registration

    assert registry.names() == (
        "dummy-service",
    )

    assert registry.services() == (
        service,
    )

    assert registry.registrations() == (
        registration,
    )

    #
    # Diagnostics.
    #
    diagnostics = cast(
        Mapping[str, Any],
        registry.diagnostics(),
    )

    assert diagnostics["service_count"] == 1

    services = cast(
        list[Mapping[str, Any]],
        diagnostics["services"],
    )

    assert len(services) == 1

    registered = services[0]

    assert registered["name"] == "dummy-service"
    assert registered["version"] == "1.0.0"
    assert registered["enabled"] is True
    assert registered["singleton"] is True
    assert registered["priority"] == 0
    assert registered["tags"] == []