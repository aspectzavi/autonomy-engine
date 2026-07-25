"""
Container contains() tests.
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


def test_container_contains() -> None:
    """
    contains() should accurately report whether
    a service has been registered.
    """

    container = Container()

    #
    # Initially empty.
    #
    assert not container.contains(
        ServiceA,
    )

    assert not container.contains(
        ServiceB,
    )

    #
    # Register one service.
    #
    container.register_singleton(
        ServiceA,
    )

    assert container.contains(
        ServiceA,
    )

    assert not container.contains(
        ServiceB,
    )

    #
    # Register another.
    #
    container.register_transient(
        ServiceB,
    )

    assert container.contains(
        ServiceA,
    )

    assert container.contains(
        ServiceB,
    )

    #
    # Clearing the container should remove both.
    #
    container.clear()

    assert not container.contains(
        ServiceA,
    )

    assert not container.contains(
        ServiceB,
    )

    assert len(container) == 0