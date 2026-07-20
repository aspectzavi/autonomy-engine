"""
Dependency injection service registration.

A registration connects a service contract with a provider and defines
the lifetime rules for the created instance.
"""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from backend.app.container.lifetime import ServiceLifetime
from backend.app.container.provider import Provider


T = TypeVar("T")


class ServiceRegistration(Generic[T]):
    """
    Defines how a service is resolved.
    """

    def __init__(
        self,
        service_type: type[T],
        provider: Provider[T],
        lifetime: ServiceLifetime,
    ) -> None:
        self.service_type = service_type

        self.provider = provider

        self.lifetime = lifetime

        self._instance: T | None = None

    # ------------------------------------------------------------------
    # Resolution
    # ------------------------------------------------------------------

    def resolve(self) -> T:
        """
        Resolve service according to lifetime.
        """

        if self.lifetime is ServiceLifetime.SINGLETON:
            if self._instance is None:
                self._instance = self.provider.provide()

            return self._instance

        if self.lifetime is ServiceLifetime.TRANSIENT:
            return self.provider.provide()

        if self.lifetime is ServiceLifetime.SCOPED:
            return self.provider.provide()

        raise RuntimeError(
            f"Unsupported service lifetime: {self.lifetime}"
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    @property
    def has_instance(self) -> bool:
        """
        Whether a singleton instance exists.
        """
        return self._instance is not None

    def diagnostics(self) -> dict[str, Any]:
        """
        Return registration diagnostics.
        """
        return {
            "service": self.service_type.__name__,
            "provider": type(self.provider).__name__,
            "lifetime": self.lifetime.value,
            "initialized": self.has_instance,
        }