"""
Capability registry.

The registry owns discovery of all capability providers.

Responsibilities:

- register providers
- unregister providers
- discover capabilities
- resolve providers
- expose diagnostics

The registry does not execute capabilities. Execution is delegated to
the appropriate provider.
"""

from __future__ import annotations

from backend.core.capabilities.capability import Capability
from backend.core.capabilities.capability_provider import (
    CapabilityProvider,
)


class CapabilityRegistry:
    """
    Registry of capability providers.
    """

    def __init__(
        self,
    ) -> None:
        self._providers: dict[
            str,
            CapabilityProvider,
        ] = {}

        self._capabilities: dict[
            str,
            CapabilityProvider,
        ] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        provider: CapabilityProvider,
    ) -> None:
        """
        Register a capability provider.
        """

        if provider.name in self._providers:
            raise ValueError(
                f"Provider '{provider.name}' already registered."
            )

        self._providers[
            provider.name
        ] = provider

        for capability in provider.capabilities:
            if capability.name in self._capabilities:
                raise ValueError(
                    f"Capability '{capability.name}' "
                    "already registered."
                )

            self._capabilities[
                capability.name
            ] = provider

    def unregister(
        self,
        provider_name: str,
    ) -> None:
        """
        Remove a provider.
        """

        provider = self._providers.pop(
            provider_name,
        )

        for capability in provider.capabilities:
            self._capabilities.pop(
                capability.name,
                None,
            )

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    @property
    def providers(
        self,
    ) -> tuple[
        CapabilityProvider,
        ...,
    ]:
        """
        Registered providers.
        """

        return tuple(
            self._providers.values(),
        )

    @property
    def capabilities(
        self,
    ) -> tuple[
        Capability,
        ...,
    ]:
        """
        Registered capabilities.
        """

        capabilities: list[
            Capability,
        ] = []

        for provider in self.providers:
            capabilities.extend(
                provider.capabilities,
            )

        return tuple(
            capabilities,
        )

    def provider_for(
        self,
        capability: str,
    ) -> CapabilityProvider:
        """
        Resolve the provider for a capability.
        """

        try:
            return self._capabilities[
                capability
            ]

        except KeyError as exc:
            raise LookupError(
                f"Unknown capability "
                f"'{capability}'."
            ) from exc

    def supports(
        self,
        capability: str,
    ) -> bool:
        """
        Whether a capability exists.
        """

        return (
            capability
            in self._capabilities
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Registry diagnostics.
        """

        return {
            "provider_count": len(
                self._providers,
            ),
            "capability_count": len(
                self._capabilities,
            ),
            "providers": tuple(
                self._providers.keys(),
            ),
            "capabilities": tuple(
                sorted(
                    self._capabilities.keys(),
                ),
            ),
        }