"""
Dependency resolver.

Responsible for automatically creating objects by resolving
constructor dependencies.
"""

from __future__ import annotations

import inspect
import types

from typing import TYPE_CHECKING, Any, get_args, get_origin, get_type_hints

from backend.app.container.exceptions import (
    CircularDependencyError,
)


if TYPE_CHECKING:
    from backend.app.container.container import Container


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

        self._resolving.add(
            service_type,
        )

        try:
            registration = (
                self._container.registration(
                    service_type,
                )
            )

            if registration is not None:
                return registration.provider.provide(
                    self._container,
                )

            return self._construct(
                service_type,
            )

        finally:
            self._resolving.remove(
                service_type,
            )

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
            service_type.__init__,
        )

        #
        # Resolve postponed annotations created by:
        #
        # from __future__ import annotations
        #
        type_hints = get_type_hints(
            service_type.__init__,
        )

        dependencies: dict[str, Any] = {}

        for name, parameter in constructor.parameters.items():

            if name == "self":
                continue

            #
            # Ignore *args and **kwargs.
            #
            if parameter.kind in (
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            ):
                continue

            annotation = type_hints.get(
                name,
            )

            #
            # Missing annotations.
            #
            if annotation is None:
                if parameter.default is not inspect.Parameter.empty:
                    continue

                raise TypeError(
                    f"Missing type annotation for "
                    f"{service_type.__name__}.{name}"
                )

            dependency_type = (
                self._unwrap_optional(
                    annotation,
                )
            )

            #
            # Unsupported annotation.
            #
            if dependency_type is None:
                if parameter.default is not inspect.Parameter.empty:
                    continue

                raise TypeError(
                    f"Unsupported dependency annotation "
                    f"for {service_type.__name__}.{name}"
                )

            #
            # Resolve dependency.
            #
            try:
                dependencies[name] = self.resolve(
                    dependency_type,
                )

            except Exception:
                #
                # Optional dependencies can safely fall back
                # to their default value.
                #
                if parameter.default is not inspect.Parameter.empty:
                    continue

                raise

        return service_type(
            **dependencies,
        )

    # ------------------------------------------------------------------
    # Type Handling
    # ------------------------------------------------------------------

    def _unwrap_optional(
        self,
        annotation: Any,
    ) -> type[Any] | None:
        """
        Extract the concrete type from Optional[T].

        Supports:

        - Service
        - Service | None
        - Optional[Service]
        """

        origin = get_origin(
            annotation,
        )

        #
        # Python 3.10+ union syntax:
        #
        # Service | None
        #
        if origin is types.UnionType:
            args = get_args(
                annotation,
            )

            non_none = [
                arg
                for arg in args
                if arg is not type(None)
            ]

            if len(non_none) == 1:
                dependency = non_none[0]

                if isinstance(
                    dependency,
                    type,
                ):
                    return dependency

            return None

        #
        # typing.Optional / typing.Union
        #
        if str(origin) == "typing.Union":
            args = get_args(
                annotation,
            )

            non_none = [
                arg
                for arg in args
                if arg is not type(None)
            ]

            if len(non_none) == 1:
                dependency = non_none[0]

                if isinstance(
                    dependency,
                    type,
                ):
                    return dependency

            return None

        #
        # Normal class dependency.
        #
        if isinstance(
            annotation,
            type,
        ):
            return annotation

        return None