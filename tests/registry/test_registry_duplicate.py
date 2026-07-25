"""
ServiceRegistry duplicate registration tests.
"""

from __future__ import annotations

import pytest

from backend.core.kernel.exceptions import (
    ServiceAlreadyRegisteredError,
)
from backend.core.kernel.metadata import ServiceMetadata
from backend.core.kernel.registry import (
    ServiceRegistration,
    ServiceRegistry,
)
from backend.core.kernel.service import KernelService


class DummyService(KernelService):
    """
    Minimal service for registry tests.
    """

    def __init__(self) -> None:
        super().__init__(
            ServiceMetadata(
                name="dummy-service",
                version="1.0.0",
            )
        )


def test_registry_duplicate() -> None:
    """
    Registering the same service twice should fail.
    """

    registry = ServiceRegistry()

    registration = ServiceRegistration(
        metadata=ServiceMetadata(
            name="dummy-service",
            version="1.0.0",
        ),
        service=DummyService(),
    )

    registry.register(registration)

    with pytest.raises(ServiceAlreadyRegisteredError):
        registry.register(registration)

    #
    # Registry should still contain exactly one service.
    #
    assert len(registry) == 1

    assert registry.contains("dummy-service")