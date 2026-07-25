"""
Capability provider.

Capability providers implement executable capabilities.

A provider may expose one or many capabilities.

Examples:

    BrowserProvider
        - browser.open
        - browser.search
        - browser.click

    FilesystemProvider
        - filesystem.read
        - filesystem.write

    PythonProvider
        - python.execute

Providers perform execution while the registry performs discovery.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from backend.core.capabilities.capability import Capability
from backend.core.capabilities.capability_result import CapabilityResult


class CapabilityProvider(ABC):
    """
    Base class for capability providers.
    """

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    @property
    @abstractmethod
    def name(
        self,
    ) -> str:
        """
        Provider name.
        """

    @property
    @abstractmethod
    def capabilities(
        self,
    ) -> tuple[Capability, ...]:
        """
        Capabilities exposed by this provider.
        """

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def supports(
        self,
        capability: str,
    ) -> bool:
        """
        Whether this provider supports the capability.
        """

        return any(
            item.name == capability
            for item in self.capabilities
        )

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    @abstractmethod
    async def execute(
        self,
        capability: str,
        *,
        arguments: dict[str, object] | None = None,
    ) -> CapabilityResult:
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
            "provider": self.name,
            "capability_count": len(
                self.capabilities,
            ),
            "capabilities": tuple(
                capability.name
                for capability in self.capabilities
            ),
        }