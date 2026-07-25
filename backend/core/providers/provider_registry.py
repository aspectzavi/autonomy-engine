"""
Provider registry.

Maintains the collection of installed providers.

Providers register themselves here during application bootstrap.

The registry is responsible only for storage and lookup. It does not
perform capability resolution.
"""

from __future__ import annotations

from backend.core.providers.provider import Provider


class ProviderRegistry:
    """
    Registry of installed providers.
    """

    def __init__(self) -> None:
        self._providers: dict[str, Provider] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        provider: Provider,
    ) -> None:
        """
        Register a provider.
        """

        if provider.name in self._providers:
            raise ValueError(
                f"Provider '{provider.name}' already registered."
            )

        self._providers[
            provider.name
        ] = provider

    def unregister(
        self,
        provider_name: str,
    ) -> None:
        """
        Remove a provider.
        """

        self._providers.pop(
            provider_name,
        )

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get(
        self,
        provider_name: str,
    ) -> Provider:
        """
        Retrieve a provider.
        """

        try:
            return self._providers[
                provider_name
            ]
        except KeyError as exc:
            raise LookupError(
                f"Unknown provider '{provider_name}'."
            ) from exc

    def providers(
        self,
    ) -> tuple[Provider, ...]:
        """
        Return all providers.
        """

        return tuple(
            self._providers.values()
        )

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def supporting(
        self,
        capability: str,
    ) -> tuple[Provider, ...]:
        """
        Return every provider supporting a capability.
        """

        return tuple(
            provider
            for provider in self._providers.values()
            if provider.supports(
                capability,
            )
        )

    def supports(
        self,
        capability: str,
    ) -> bool:
        """
        Whether any provider supports a capability.
        """

        return any(
            provider.supports(
                capability,
            )
            for provider in self._providers.values()
        )

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def __contains__(
        self,
        provider_name: str,
    ) -> bool:
        return (
            provider_name
            in self._providers
        )

    def __len__(
        self,
    ) -> int:
        return len(
            self._providers,
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
                self,
            ),
            "providers": tuple(
                provider.metadata.diagnostics()
                for provider in self.providers()
            ),
        }