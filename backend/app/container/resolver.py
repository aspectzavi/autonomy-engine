"""
Dependency resolver.

Responsible for automatically creating objects by resolving
constructor dependencies.
"""

from __future__ import annotations

import inspect
from typing import Any

from backend.app.container.container import Container
from backend.app.container.exceptions import (
    CircularDependencyError,
)


class DependencyResolver:
    """
    Resolves objects using constructor injection.
    """

    def __init__(
        self,
        container: Container,
    ) -> None:
        self._container = container

        self._resolving: set[type[Any]] = set()

    # ------------------------------------------------------------------
    # Resolution
    # ------------------------------------------------------------------

    def resolve(
        self,
        service_type: type[Any],
    ) -> Any:
        """
        Resolve a service and its dependencies.
        """

        if service_type in self._resolving:
            raise CircularDependencyError(
                f"Circular dependency detected for "
                f"{service_type.__name__}"
            )

        self._resolving.add(service_type)

        try:
            if self._container.contains(service_type):
                return self._container.resolve(service_type)

            return self._construct(service_type)

        finally:
            self._resolving.remove(service_type)

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def _construct(
        self,
        service_type: type[Any],
    ) -> Any:
        """
        Construct an object using constructor injection.
        """

        constructor = inspect.signature(
            service_type.__init__
        )

        dependencies: dict[str, Any] = {}

        for name, parameter in constructor.parameters.items():

            if name == "self":
                continue

            if parameter.annotation is inspect.Parameter.empty:
                raise TypeError(
                    f"Missing type annotation for "
                    f"{service_type.__name__}.{name}"
                )

            dependencies[name] = self.resolve(
                parameter.annotation
            )

        return service_type(**dependencies)