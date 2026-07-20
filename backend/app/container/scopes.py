"""
Dependency injection scopes.

Scopes provide isolated lifetimes for scoped services.

A scope represents a child resolution context where scoped services
are cached independently from the parent container.
"""

from __future__ import annotations

from typing import Any, TypeVar, cast

from backend.app.container.container import Container
from backend.app.container.registration import ServiceRegistration
from backend.app.container.lifetime import ServiceLifetime


T = TypeVar("T")


class Scope:
    """
    Scoped dependency resolution context.

    Scoped instances live only for the lifetime of this scope.
    """

    def __init__(
        self,
        container: Container,
    ) -> None:
        self._container = container

        self._instances: dict[type[Any], Any] = {}

        self._disposed = False

    # ------------------------------------------------------------------
    # Resolution
    # ------------------------------------------------------------------

    def resolve(
        self,
        service_type: type[T],
    ) -> T:
        """
        Resolve a service inside this scope.
        """

        self._ensure_active()

        registration = self._get_registration(
            service_type
        )

        if registration is None:
            return self._container.resolve(
                service_type
            )

        if registration.lifetime is ServiceLifetime.SCOPED:
            if service_type not in self._instances:
                self._instances[service_type] = (
                    registration.provider.provide()
                )

            return cast(
                T,
                self._instances[service_type],
            )

        return self._container.resolve(
            service_type
        )

    # ------------------------------------------------------------------
    # Registration Lookup
    # ------------------------------------------------------------------

    def _get_registration(
        self,
        service_type: type[Any],
    ) -> ServiceRegistration[Any] | None:
        """
        Find a registration in the parent container.
        """

        for registration in self._container.registrations():
            if registration.service_type is service_type:
                return registration

        return None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def dispose(self) -> None:
        """
        Dispose the scope and clear scoped instances.
        """

        if self._disposed:
            return

        self._instances.clear()

        self._disposed = True

    def _ensure_active(self) -> None:
        """
        Ensure the scope has not been disposed.
        """

        if self._disposed:
            raise RuntimeError(
                "Scope has already been disposed."
            )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return scope diagnostics.
        """
        return {
            "disposed": self._disposed,
            "instance_count": len(self._instances),
            "instances": [
                service.__name__
                for service in self._instances
            ],
        }

    def __enter__(self) -> "Scope":
        """
        Enter scope context.
        """
        self._ensure_active()

        return self

    def __exit__(
        self,
        exc_type: object,
        exc_value: object,
        traceback: object,
    ) -> None:
        """
        Exit scope context.
        """
        self.dispose()