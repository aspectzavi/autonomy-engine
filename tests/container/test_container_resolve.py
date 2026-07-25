"""
Container resolution tests.
"""

from __future__ import annotations

from backend.app.container.container import Container


class Repository:
    """
    Simple dependency.
    """


class Service:
    """
    Depends on Repository.
    """

    def __init__(
        self,
        repository: Repository,
    ) -> None:
        self.repository = repository


def test_container_resolve() -> None:
    """
    The container should resolve registered services
    and automatically inject constructor dependencies.
    """

    container = Container()

    container.register_singleton(
        Repository,
    )

    container.register_singleton(
        Service,
    )

    service = container.resolve(
        Service,
    )

    #
    # Correct types.
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
    # Singleton dependency should be reused.
    #
    repository = container.resolve(
        Repository,
    )

    assert service.repository is repository

    #
    # Resolving the service again should return
    # the same singleton instance.
    #
    service_again = container.resolve(
        Service,
    )

    assert service_again is service