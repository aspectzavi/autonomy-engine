"""
Dependency injection decorators.

Decorators attach registration metadata to classes
without coupling them directly to the container.
"""

from __future__ import annotations

from typing import Any, TypeVar

from backend.app.container.lifetime import ServiceLifetime


T = TypeVar("T")


def singleton(
    cls: type[T],
) -> type[T]:
    """
    Mark a class as singleton service.
    """
    setattr(
        cls,
        "__di_lifetime__",
        ServiceLifetime.SINGLETON,
    )

    return cls


def transient(
    cls: type[T],
) -> type[T]:
    """
    Mark a class as transient service.
    """
    setattr(
        cls,
        "__di_lifetime__",
        ServiceLifetime.TRANSIENT,
    )

    return cls


def scoped(
    cls: type[T],
) -> type[T]:
    """
    Mark a class as scoped service.
    """
    setattr(
        cls,
        "__di_lifetime__",
        ServiceLifetime.SCOPED,
    )

    return cls


def inject(
    cls: type[T],
) -> type[T]:
    """
    Mark a class for constructor injection.

    This flag is used by the resolver during
    automatic dependency construction.
    """
    setattr(
        cls,
        "__di_inject__",
        True,
    )

    return cls


def get_lifetime(
    cls: type[Any],
) -> ServiceLifetime | None:
    """
    Retrieve declared service lifetime.
    """
    value = getattr(
        cls,
        "__di_lifetime__",
        None,
    )

    if isinstance(value, ServiceLifetime):
        return value

    return None


def is_injectable(
    cls: type[Any],
) -> bool:
    """
    Check whether a class supports injection.
    """
    return bool(
        getattr(
            cls,
            "__di_inject__",
            False,
        )
    )