"""
Container singleton lifetime tests.
"""

from __future__ import annotations

from backend.app.container.container import Container


class CounterService:
    """
    Service used to verify singleton lifetime.
    """

    created = 0

    def __init__(self) -> None:
        type(self).created += 1


def test_container_singleton() -> None:
    """
    Singleton registrations should always return
    the same instance.
    """

    CounterService.created = 0

    container = Container()

    container.register_singleton(
        CounterService,
    )

    first = container.resolve(
        CounterService,
    )

    second = container.resolve(
        CounterService,
    )

    third = container.resolve(
        CounterService,
    )

    #
    # Same object every time.
    #
    assert first is second
    assert second is third

    #
    # Constructor should have executed only once.
    #
    assert CounterService.created == 1

    #
    # Registration should now own an initialized instance.
    #
    registration = container.registration(
        CounterService,
    )

    assert registration is not None
    assert registration.has_instance