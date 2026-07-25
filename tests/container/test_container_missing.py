"""
Container missing registration tests.
"""

from __future__ import annotations

from backend.app.container.container import Container


class Repository:
    """
    Unregistered dependency.
    """


class Service:
    """
    Unregistered service depending on Repository.
    """

    def __init__(
        self,
        repository: Repository,
    ) -> None:
        self.repository = repository


def test_container_missing() -> None:
    """
    The container should automatically construct
    unregistered classes using constructor injection.
    """

    container = Container()

    service = container.resolve(
        Service,
    )

    #
    # Objects should still be created.
    #
    assert isinstance(
        service,
        Service,
    )

    assert isinstance(
        service.repository,
        Repository,
    )

    #
    # Automatic construction should not register
    # the service in the container.
    #
    assert not container.contains(
        Service,
    )

    assert not container.contains(
        Repository,
    )

    assert len(container) == 0