"""
ServiceRegistry lookup tests.
"""

from __future__ import annotations

from backend.core.kernel.metadata import ServiceMetadata
from backend.core.kernel.registry import (
    ServiceRegistration,
    ServiceRegistry,
)
from backend.core.kernel.service import KernelService


class DummyService(KernelService):
    """
    Simple service used for registry lookup tests.
    """

    def __init__(self) -> None:
        super().__init__(
            ServiceMetadata(
                name="lookup-service",
                version="1.0.0",
            ),
        )


def test_registry_lookup() -> None:
    """
    Registered services should be retrievable by name.
    """

    registry = ServiceRegistry()

    service = DummyService()

    registration = ServiceRegistration(
        metadata=service.metadata,
        service=service,
    )

    registry.register(registration)

    #
    # Membership.
    #
    assert "lookup-service" in registry
    assert registry.contains("lookup-service")

    #
    # get() returns the original instance.
    #
    resolved = registry.get("lookup-service")

    assert resolved is service

    #
    # registration() returns the original registration.
    #
    resolved_registration = registry.registration(
        "lookup-service",
    )

    assert resolved_registration is registration
    assert resolved_registration.service is service
    assert resolved_registration.metadata.name == "lookup-service"
    assert resolved_registration.metadata.version == "1.0.0"

    #
    # Enumeration.
    #
    assert registry.services() == (service,)
    assert registry.registrations() == (registration,)
    assert registry.names() == ("lookup-service",)