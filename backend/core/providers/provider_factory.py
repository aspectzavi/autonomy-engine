"""
Provider factory.

Resolves providers capable of executing a requested capability.

The factory sits between the capability layer and the provider layer.

Architecture

CapabilityTask
        │
        ▼
ProviderFactory
        │
        ▼
ProviderRegistry
        │
        ▼
Concrete Provider
"""

from __future__ import annotations

from backend.core.providers.provider import Provider
from backend.core.providers.provider_registry import (
    ProviderRegistry,
)


class ProviderFactory:
    """
    Resolves providers for capabilities.
    """

    def __init__(
        self,
        *,
        registry: ProviderRegistry,
    ) -> None:
        self._registry = registry

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def registry(
        self,
    ) -> ProviderRegistry:
        """
        Provider registry.
        """

        return self._registry

    # ------------------------------------------------------------------
    # Resolution
    # ------------------------------------------------------------------

    def resolve(
        self,
        capability: str,
    ) -> Provider:
        """
        Resolve the provider responsible for a capability.
        """

        providers = self.registry.supporting(
            capability,
        )

        if not providers:
            raise LookupError(
                f"No provider supports capability "
                f"'{capability}'."
            )

        #
        # Future versions can implement provider
        # prioritization, configuration, or load
        # balancing here.
        #
        return providers[0]

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Factory diagnostics.
        """

        return {
            "registry": (
                self.registry.diagnostics()
            ),
        }