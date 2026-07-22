"""
Dependency injection providers.

Providers define how service instances are created.

Supported creation strategies:

- class construction
- factory functions
- existing instances
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Generic, TypeVar, cast


if TYPE_CHECKING:
    from backend.app.container.container import Container


T = TypeVar("T")


class Provider(Generic[T]):
    """
    Base provider abstraction.
    """

    def provide(
        self,
        container: Container,
    ) -> T:
        """
        Create or return a service instance.
        """
        raise NotImplementedError


class ClassProvider(Provider[T]):
    """
    Provider that constructs a class.

    Uses the dependency resolver from the container
    to perform constructor injection.
    """

    def __init__(
        self,
        implementation: type[T],
    ) -> None:
        self._implementation = implementation

    def provide(
        self,
        container: Container,
    ) -> T:
        """
        Instantiate using container injection.
        """

        return cast(
            T,
            container._resolver._construct(
                self._implementation,
            ),
        )


class FactoryProvider(Provider[T]):
    """
    Provider backed by a factory callable.
    """

    def __init__(
        self,
        factory: Callable[[], T],
    ) -> None:
        self._factory = factory

    def provide(
        self,
        container: Container,
    ) -> T:
        """
        Execute factory.
        """

        return self._factory()


class InstanceProvider(Provider[T]):
    """
    Provider returning an existing instance.
    """

    def __init__(
        self,
        instance: T,
    ) -> None:
        self._instance = instance

    def provide(
        self,
        container: Container,
    ) -> T:
        """
        Return stored instance.
        """

        return self._instance