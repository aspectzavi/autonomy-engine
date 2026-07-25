"""
Container clear() tests.
"""

from __future__ import annotations

from backend.app.container.container import Container


class ServiceA:
    """
    Dummy service A.
    """


class ServiceB:
    """
    Dummy service B.
    """


def test_container_clear() -> None:
    """
    Clearing the container should remove every
    registration and reset diagnostics.
    """

    container = Container()

    container.register_singleton(
        ServiceA,
    )

    container.register_transient(
        ServiceB,
    )

    #
    # Verify registrations exist.
    #
    assert len(container) == 2

    assert container.registration(
        ServiceA,
    ) is not None

    assert container.registration(
        ServiceB,
    ) is not None

    diagnostics = container.diagnostics()

    assert diagnostics["service_count"] == 2

    services = diagnostics["services"]

    assert isinstance(
        services,
        list,
    )

    assert len(services) == 2

    #
    # Clear everything.
    #
    container.clear()

    #
    # Registration table should now be empty.
    #
    assert len(container) == 0

    assert not container.contains(
        ServiceA,
    )

    assert not container.contains(
        ServiceB,
    )

    assert (
        container.registration(
            ServiceA,
        )
        is None
    )

    assert (
        container.registration(
            ServiceB,
        )
        is None
    )

    diagnostics = container.diagnostics()

    assert diagnostics["service_count"] == 0
    assert diagnostics["services"] == []