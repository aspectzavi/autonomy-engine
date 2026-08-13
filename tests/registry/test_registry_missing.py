"""
ServiceRegistry missing service tests.
"""

from __future__ import annotations

import pytest

from backend.core.kernel.exceptions import ServiceNotFoundError
from backend.core.kernel.registry import ServiceRegistry


def test_registry_missing() -> None:
    """
    Looking up a missing service should raise
    ServiceNotFoundError.
    """

    registry = ServiceRegistry()

    #
    # Registry starts empty.
    #
    assert len(registry) == 0
    assert registry.names() == ()

    #
    # get()
    #
    with pytest.raises(ServiceNotFoundError):
        registry.get("missing-service")

    #
    # registration()
    #
    with pytest.raises(ServiceNotFoundError):
        registry.registration("missing-service")

    #
    # unregister()
    #
    with pytest.raises(ServiceNotFoundError):
        registry.unregister("missing-service")

    #
    # Membership checks.
    #
    assert "missing-service" not in registry
    assert not registry.contains("missing-service")