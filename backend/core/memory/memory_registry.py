"""
Memory registry.

Maintains the collection of registered memory providers.

The registry allows the runtime to switch between different memory
implementations without affecting the rest of the autonomy engine.
"""

from __future__ import annotations

from backend.core.memory.memory_provider import MemoryProvider


class MemoryRegistry:
    """
    Registry of memory providers.
    """

    def __init__(
        self,
    ) -> None:
        self._providers: dict[str, MemoryProvider] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        *,
        name: str,
        provider: MemoryProvider,
    ) -> None:
        """
        Register a memory provider.
        """

        self._providers[name] = provider

    def unregister(
        self,
        name: str,
    ) -> None:
        """
        Remove a provider.
        """

        self._providers.pop(
            name,
            None,
        )

    # ------------------------------------------------------------------
    # Resolution
    # ------------------------------------------------------------------

    def provider(
        self,
        name: str,
    ) -> MemoryProvider:
        """
        Resolve a provider.
        """

        try:
            return self._providers[name]

        except KeyError as exc:
            raise ValueError(
                f"Unknown memory provider: {name}"
            ) from exc

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Determine whether a provider exists.
        """

        return (
            name
            in self._providers
        )

    @property
    def names(
        self,
    ) -> tuple[str, ...]:
        """
        Registered provider names.
        """

        return tuple(
            sorted(
                self._providers.keys(),
            ),
        )

    @property
    def count(
        self,
    ) -> int:
        """
        Number of registered providers.
        """

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
            "count": self.count,
            "providers": self.names,
        }