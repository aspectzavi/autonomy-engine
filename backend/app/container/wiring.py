"""
Dependency injection wiring.

Responsible for registering decorated services
into the dependency injection container.
"""

from __future__ import annotations

from typing import Any, Iterable

from backend.app.container.container import Container
from backend.app.container.decorators import get_lifetime
from backend.app.container.provider import ClassProvider
from backend.app.container.registration import ServiceRegistration
from backend.app.container.lifetime import ServiceLifetime


class ContainerWiring:
    """
    Registers discovered services into a container.
    """

    def __init__(
        self,
        container: Container,
    ) -> None:
        self._container = container

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register_services(
        self,
        services: Iterable[type[Any]],
    ) -> None:
        """
        Register decorated service classes.
        """

        for service in services:
            lifetime = get_lifetime(service)

            if lifetime is None:
                continue

            self._register(
                service,
                lifetime,
            )

    def _register(
        self,
        service: type[Any],
        lifetime: ServiceLifetime,
    ) -> None:
        """
        Register a single service.
        """

        registration = ServiceRegistration(
            service_type=service,
            provider=ClassProvider(service),
            lifetime=lifetime,
        )

        self._container.register(
            registration
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return wiring diagnostics.
        """
        return {
            "registered_services": len(
                self._container
            ),
        }