"""
Capability.

Represents a single executable capability that can be exposed by the
autonomy engine.

Capabilities are high-level actions understood by the planner, such as:

    browser.search
    browser.click
    filesystem.read
    python.execute
    api.call

A capability does not execute work itself. Instead, it describes what
can be executed and delegates implementation to a provider.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from backend.core.capabilities.capability_metadata import (
    CapabilityMetadata,
)


@dataclass(frozen=True, slots=True)
class Capability:
    """
    Executable capability definition.
    """

    #
    # Unique capability identifier.
    #
    name: str

    #
    # Human-readable description.
    #
    description: str

    #
    # Metadata describing the capability.
    #
    metadata: CapabilityMetadata = field(
        default_factory=CapabilityMetadata,
    )

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    @property
    def category(
        self,
    ) -> str:
        """
        Capability category.

        Example:

            browser.search -> browser
        """

        return self.name.partition(".")[0]

    @property
    def operation(
        self,
    ) -> str:
        """
        Capability operation.

        Example:

            browser.search -> search
        """

        return self.name.partition(".")[2]

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return capability diagnostics.
        """

        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "operation": self.operation,
            "metadata": self.metadata.diagnostics(),
        }