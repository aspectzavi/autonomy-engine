"""
Dependency injection container.

The container is the central dependency resolution entry point.

Responsibilities:

- registering services
- resolving services
- managing service lifetimes
- delegating constructor injection

The container does not:
- manage application startup
- control service lifecycle

Complex object construction is handled by DependencyResolver.
"""

from __future__ import annotations

from typing import Any, TypeVar, cast

from backend.app.container.exceptions import (
    ServiceAlreadyRegisteredError,
)
from backend.app.container.lifetime import ServiceLifetime
from backend.app.container.provider import (
    ClassProvider,
    InstanceProvider,
)
from backend.app.container.registration import ServiceRegistration
from backend.app.container.resolver import DependencyResolver
from backend.app.container.scopes import Scope


T = TypeVar("T")


class Container:
    """
    Dependency injection container.

    Stores service registrations and resolves instances through
    providers and the dependency resolver.
    """

    def __init__(self) -> None:
        self._registrations: dict[
            type[Any],
            ServiceRegistration[Any],
        ] = {}

        self._resolver = DependencyResolver(self)

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        registration: ServiceRegistration[Any],
    ) -> None:
        """
        Register a service.

        Raises:
            ServiceAlreadyRegisteredError:
                If the service already exists.
        """
        service_type = registration.service_type

        if service_type in self._registrations:
            raise ServiceAlreadyRegisteredError(
                f"Service '{service_type.__name__}' already registered."
            )

        self._registrations[service_type] = registration

    def register_singleton(
        self,
        service_type: type[T],
        implementation: type[T] | None = None,
    ) -> None:
        """
        Register a singleton service.
        """
        self.register(
            ServiceRegistration(
                service_type=service_type,
                provider=ClassProvider(
                    implementation or service_type
                ),
                lifetime=ServiceLifetime.SINGLETON,
            )
        )

    def register_transient(
        self,
        service_type: type[T],
        implementation: type[T] | None = None,
    ) -> None:
        """
        Register a transient service.
        """
        self.register(
            ServiceRegistration(
                service_type=service_type,
                provider=ClassProvider(
                    implementation or service_type
                ),
                lifetime=ServiceLifetime.TRANSIENT,
            )
        )

    def register_instance(
        self,
        service_type: type[T],
        instance: T,
    ) -> None:
        """
        Register an existing singleton instance.

        Existing registrations are replaced because instance
        registrations are explicit composition-root overrides.
        """

        self._registrations[service_type] = ServiceRegistration(
            service_type=service_type,
            provider=InstanceProvider(
                instance,
            ),
            lifetime=ServiceLifetime.SINGLETON,
        )

    # ------------------------------------------------------------------
    # Resolution
    # ------------------------------------------------------------------

    def resolve(
        self,
        service_type: type[T],
    ) -> T:
        """
        Resolve a service.

        Supports:

        - registered services
        - automatic constructor injection
        """
        return cast(
            T,
            self._resolver.resolve(service_type),
        )

        # ------------------------------------------------------------------
    # Scopes
    # ------------------------------------------------------------------

    def create_scope(
        self,
    ) -> Scope:
        """
        Create a new dependency resolution scope.
        """
        return Scope(self)

    # ------------------------------------------------------------------
    # Inspection
    # ------------------------------------------------------------------

    def contains(
        self,
        service_type: type[Any],
    ) -> bool:
        """
        Check whether a service is registered.
        """
        return service_type in self._registrations

    def registration(
        self,
        service_type: type[Any],
    ) -> ServiceRegistration[Any] | None:
        """
        Return service registration if available.
        """
        return self._registrations.get(
            service_type,
        )

    def registrations(
        self,
    ) -> tuple[ServiceRegistration[Any], ...]:
        """
        Return all registrations.
        """
        return tuple(self._registrations.values())

    def clear(
        self,
    ) -> None:
        """
        Remove all registrations.
        """
        self._registrations.clear()

    def __len__(
        self,
    ) -> int:
        """
        Number of registered services.
        """
        return len(self._registrations)

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return container diagnostics.
        """
        return {
            "service_count": len(self),
            "services": [
                {
                    "service": registration.service_type.__name__,
                    "provider": type(
                        registration.provider
                    ).__name__,
                    "lifetime": registration.lifetime.value,
                }
                for registration in self._registrations.values()
            ],
        }