"""
ServiceRegistry validation tests.
"""

from __future__ import annotations

import pytest

from backend.core.kernel.exceptions import RegistryError
from backend.core.kernel.metadata import ServiceMetadata
from backend.core.kernel.registry import (
    ServiceRegistration,
    ServiceRegistry,
)
from backend.core.kernel.service import KernelService


class DummyService(KernelService):
    """
    Simple service used for registry validation tests.
    """

    def __init__(self) -> None:
        super().__init__(
            ServiceMetadata(
                name="dummy-service",
                version="1.0.0",
            ),
        )


def test_registry_validation() -> None:
    """
    Registry validation should succeed for valid
    registrations and fail when a registration has
    no service instance.
    """

    #
    # Valid registry.
    #
    registry = ServiceRegistry()

    service = DummyService()

    registry.register(
        ServiceRegistration(
            metadata=service.metadata,
            service=service,
        )
    )

    #
    # Should not raise.
    #
    registry.validate()

    #
    # Invalid registry (service instance is None).
    #
    invalid_registry = ServiceRegistry()

    invalid_registry.register(
        ServiceRegistration(
            metadata=ServiceMetadata(
                name="broken-service",
                version="1.0.0",
            ),
            service=None,  # type: ignore[arg-type]
        )
    )

    with pytest.raises(RegistryError):
        invalid_registry.validate()