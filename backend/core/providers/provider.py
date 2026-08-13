"""
Abstract provider.

A Provider is responsible for executing one or more capabilities.

Providers encapsulate integrations with external systems such as
browsers, filesystems, shells, Python execution environments,
vision models, or remote APIs.

Providers own implementation.

Capabilities own intent.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from backend.core.providers.provider_metadata import (
    ProviderMetadata,
)
from backend.core.providers.provider_result import (
    ProviderResult,
)


class Provider(ABC):
    """
    Abstract base class for all providers.
    """

    def __init__(
        self,
        metadata: ProviderMetadata,
    ) -> None:
        self._metadata = metadata

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def metadata(
        self,
    ) -> ProviderMetadata:
        """
        Provider metadata.
        """

        return self._metadata

    @property
    def name(
        self,
    ) -> str:
        """
        Provider name.
        """

        return self.metadata.name

    @property
    def version(
        self,
    ) -> str:
        """
        Provider version.
        """

        return self.metadata.version

    # ------------------------------------------------------------------
    # Capability Queries
    # ------------------------------------------------------------------

    @abstractmethod
    def supports(
        self,
        capability: str,
    ) -> bool:
        """
        Determine whether this provider supports a capability.
        """

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    @abstractmethod
    async def execute(
        self,
        capability: str,
        *,
        arguments: dict[str, object] | None = None,
    ) -> ProviderResult:
        """
        Execute a capability.
        """

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Provider diagnostics.
        """

        return {
            "metadata": self.metadata.diagnostics(),
        }