"""
ServiceRegistry unregister tests.
"""

from __future__ import annotations

import pytest

from backend.core.kernel.exceptions import ServiceNotFoundError
from backend.core.kernel.metadata import ServiceMetadata
from backend.core.kernel.registry import (
    ServiceRegistration,
    ServiceRegistry,
)
from backend.core.kernel.service import KernelService


class DummyService(KernelService):
    """
    Minimal service for registry testing.
    """

    def __init__(self) -> None:
        super().__init__(
            ServiceMetadata(
                name="dummy-service",
                version="1.0.0",
            ),
        )


def test_registry_unregister() -> None:
    """
    Unregistering a service should remove it
    from the registry.
    """

    registry = ServiceRegistry()

    service = DummyService()

    registration = ServiceRegistration(
        metadata=service.metadata,
        service=service,
    )

    registry.register(registration)

    assert len(registry) == 1
    assert registry.contains("dummy-service")

    registry.unregister("dummy-service")

    assert len(registry) == 0
    assert not registry.contains("dummy-service")

    with pytest.raises(ServiceNotFoundError):
        registry.get("dummy-service")