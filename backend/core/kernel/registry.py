"""
Kernel service registry.

The service registry is the central catalog of all runtime-managed
services.

Its responsibilities are intentionally limited to:

- service registration
- service lookup
- service removal
- service enumeration
- registry diagnostics

The registry does NOT:

- start services
- stop services
- resolve dependency order
- instantiate services
- perform dependency injection

Those responsibilities belong to the Runtime and DependencyGraph.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from backend.core.kernel.exceptions import (
    RegistryError,
    ServiceAlreadyRegisteredError,
    ServiceNotFoundError,
)
from backend.core.kernel.metadata import ServiceMetadata
from backend.core.kernel.service import KernelService


@dataclass(slots=True, frozen=True)
class ServiceRegistration:
    """
    Immutable service registration.

    This model contains all metadata required by the runtime
    to understand a registered service.
    """

    metadata: ServiceMetadata

    service: KernelService

    singleton: bool = True

    enabled: bool = True

    priority: int = 0

    tags: frozenset[str] = field(default_factory=frozenset)

    attributes: dict[str, Any] = field(default_factory=dict)


class ServiceRegistry:
    """
    Registry of kernel-managed services.
    """

    def __init__(self) -> None:
        self._services: dict[str, ServiceRegistration] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        registration: ServiceRegistration,
    ) -> None:
        """
        Register a service.

        Raises:
            ServiceAlreadyRegisteredError:
                If a service with the same name already exists.
        """
        name = registration.metadata.name

        if name in self._services:
            raise ServiceAlreadyRegisteredError(
                f"Service '{name}' is already registered."
            )

        self._services[name] = registration

    def unregister(
        self,
        name: str,
    ) -> None:
        """
        Remove a service from the registry.
        """
        if name not in self._services:
            raise ServiceNotFoundError(
                f"Service '{name}' is not registered."
            )

        del self._services[name]

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get(
        self,
        name: str,
    ) -> KernelService:
        """
        Retrieve a registered service.
        """
        registration = self._services.get(name)

        if registration is None:
            raise ServiceNotFoundError(
                f"Service '{name}' is not registered."
            )

        return registration.service

    def registration(
        self,
        name: str,
    ) -> ServiceRegistration:
        """
        Retrieve the registration for a service.
        """
        registration = self._services.get(name)

        if registration is None:
            raise ServiceNotFoundError(
                f"Service '{name}' is not registered."
            )

        return registration

    # ------------------------------------------------------------------
    # Enumeration
    # ------------------------------------------------------------------

    def services(self) -> tuple[KernelService, ...]:
        """
        Return all registered service instances.
        """
        return tuple(
            registration.service
            for registration in self._services.values()
        )

    def registrations(self) -> tuple[ServiceRegistration, ...]:
        """
        Return all registrations.
        """
        return tuple(self._services.values())

    def names(self) -> tuple[str, ...]:
        """
        Return all registered service names.
        """
        return tuple(sorted(self._services.keys()))

    def find_by_tag(
        self,
        tag: str,
    ) -> tuple[KernelService, ...]:
        """
        Return services having a specific tag.
        """
        return tuple(
            registration.service
            for registration in self._services.values()
            if tag in registration.tags
        )

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Determine whether a service exists.
        """
        return name in self._services

    def clear(self) -> None:
        """
        Remove every registered service.
        """
        self._services.clear()

    def __len__(self) -> int:
        """
        Number of registered services.
        """
        return len(self._services)

    def __contains__(
        self,
        name: object,
    ) -> bool:
        """
        Membership test.
        """
        if not isinstance(name, str):
            return False

        return name in self._services

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(self) -> dict[str, Any]:
        """
        Return registry diagnostics.
        """
        return {
            "service_count": len(self),
            "services": [
                {
                    "name": registration.metadata.name,
                    "version": registration.metadata.version,
                    "enabled": registration.enabled,
                    "singleton": registration.singleton,
                    "priority": registration.priority,
                    "tags": sorted(registration.tags),
                }
                for registration in self._services.values()
            ],
        }

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self) -> None:
        """
        Validate registry integrity.
        """
        for registration in self._services.values():
            if registration.service is None:
                raise RegistryError(
                    f"Service '{registration.metadata.name}' "
                    "has no instance."
                )