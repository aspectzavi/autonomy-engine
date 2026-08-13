"""
Container factory provider tests.
"""

from __future__ import annotations

from backend.app.container.container import Container
from backend.app.container.lifetime import ServiceLifetime
from backend.app.container.provider import FactoryProvider
from backend.app.container.registration import ServiceRegistration


class Configuration:
    """
    Example object created by a factory.
    """

    created = 0

    def __init__(
        self,
        environment: str,
    ) -> None:
        type(self).created += 1
        self.environment = environment


def test_container_factory() -> None:
    """
    Factory providers should be used to construct
    registered services.
    """

    Configuration.created = 0

    container = Container()

    registration = ServiceRegistration(
        service_type=Configuration,
        provider=FactoryProvider(
            lambda: Configuration("production"),
        ),
        lifetime=ServiceLifetime.SINGLETON,
    )

    container.register(
        registration,
    )

    first = container.resolve(
        Configuration,
    )

    second = container.resolve(
        Configuration,
    )

    #
    # Singleton lifetime should cache
    # the factory-created object.
    #
    assert first is second

    assert first.environment == "production"

    #
    # Factory should only execute once.
    #
    assert Configuration.created == 1

    assert registration.has_instance