"""
Container transient lifetime tests.
"""

from __future__ import annotations

from backend.app.container.container import Container


class CounterService:
    """
    Service used to verify transient lifetime.
    """

    created = 0

    def __init__(self) -> None:
        type(self).created += 1


def test_container_transient() -> None:
    """
    Transient registrations should create a new
    instance every time they are resolved.
    """

    CounterService.created = 0

    container = Container()

    container.register_transient(
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
    # Every resolve should produce a new object.
    #
    assert first is not second
    assert second is not third
    assert first is not third

    #
    # Constructor should have executed once
    # per resolution.
    #
    assert CounterService.created == 3

    #
    # Transient registrations never cache instances.
    #
    registration = container.registration(
        CounterService,
    )

    assert registration is not None
    assert not registration.has_instance