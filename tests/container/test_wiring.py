"""
Container wiring tests.
"""

from __future__ import annotations

from backend.app.container.container import Container
from backend.app.container.decorators import singleton
from backend.app.container.lifetime import ServiceLifetime
from backend.app.container.wiring import ContainerWiring


@singleton
class RegisteredService:
    """
    Decorated service.
    """


class PlainClass:
    """
    Undecorated class.
    """


def test_container_wiring() -> None:
    """
    ContainerWiring should register only decorated
    services into the container.
    """

    container = Container()

    wiring = ContainerWiring(
        container,
    )

    wiring.register_services(
        [
            RegisteredService,
            PlainClass,
        ],
    )

    #
    # Decorated service should be registered.
    #
    assert container.contains(
        RegisteredService,
    )

    registration = container.registration(
        RegisteredService,
    )

    assert registration is not None

    assert (
        registration.lifetime
        is ServiceLifetime.SINGLETON
    )

    #
    # Undecorated class should be ignored.
    #
    assert not container.contains(
        PlainClass,
    )

    #
    # Diagnostics.
    #
    diagnostics = wiring.diagnostics()

    assert diagnostics["registered_services"] == 1