"""
Container registration tests.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

from backend.app.container.container import Container
from backend.app.container.lifetime import ServiceLifetime
from backend.app.container.provider import ClassProvider
from backend.app.container.registration import ServiceRegistration


class DummyService:
    """
    Simple service used for container tests.
    """


def test_container_register() -> None:
    """
    Registering a service should make it discoverable
    through every inspection API.
    """

    container = Container()

    #
    # Initially empty.
    #
    assert len(container) == 0
    assert not container.contains(DummyService)
    assert container.registration(DummyService) is None
    assert container.registrations() == ()

    #
    # Register a service.
    #
    registration = ServiceRegistration(
        service_type=DummyService,
        provider=ClassProvider(DummyService),
        lifetime=ServiceLifetime.SINGLETON,
    )

    container.register(registration)

    #
    # Container state.
    #
    assert len(container) == 1
    assert container.contains(DummyService)

    stored = container.registration(DummyService)

    assert stored is registration

    registrations = container.registrations()

    assert registrations == (registration,)

    #
    # Diagnostics.
    #
    diagnostics = cast(
        Mapping[str, Any],
        container.diagnostics(),
    )

    assert diagnostics["service_count"] == 1

    services = cast(
        list[Mapping[str, Any]],
        diagnostics["services"],
    )

    assert len(services) == 1

    service = services[0]

    assert service["service"] == "DummyService"
    assert service["provider"] == "ClassProvider"
    assert (
        service["lifetime"]
        == ServiceLifetime.SINGLETON.value
    )