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
from typing import Generic, TypeVar


T = TypeVar("T")


class Provider(Generic[T]):
    """
    Base provider abstraction.
    """

    def provide(self) -> T:
        """
        Create or return a service instance.
        """
        raise NotImplementedError


class ClassProvider(Provider[T]):
    """
    Provider that constructs a class.
    """

    def __init__(
        self,
        implementation: type[T],
    ) -> None:
        self._implementation = implementation

    def provide(self) -> T:
        """
        Instantiate the implementation.
        """
        return self._implementation()


class FactoryProvider(Provider[T]):
    """
    Provider backed by a factory callable.
    """

    def __init__(
        self,
        factory: Callable[[], T],
    ) -> None:
        self._factory = factory

    def provide(self) -> T:
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

    def provide(self) -> T:
        """
        Return stored instance.
        """
        return self._instance