"""
Capability metadata.

Describes static information about a capability.

Metadata is used by planners, registries, providers, and diagnostics to
understand what a capability requires without knowing its underlying
implementation.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class CapabilityMetadata:
    """
    Metadata describing a capability.
    """

    #
    # Capability version.
    #
    version: str = "1.0.0"

    #
    # Whether the capability may modify external state.
    #
    destructive: bool = False

    #
    # Whether execution requires user confirmation.
    #
    requires_confirmation: bool = False

    #
    # Whether the capability performs network operations.
    #
    network_access: bool = False

    #
    # Whether the capability requires local filesystem access.
    #
    filesystem_access: bool = False

    #
    # Whether the capability launches or controls applications.
    #
    system_access: bool = False

    #
    # Human-readable tags.
    #
    tags: frozenset[str] = field(
        default_factory=frozenset,
    )

    #
    # Arbitrary provider-specific metadata.
    #
    attributes: dict[str, object] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    @property
    def safe(self) -> bool:
        """
        Whether the capability is considered safe to execute without
        modifying the system.
        """

        return not (
            self.destructive
            or self.system_access
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return metadata diagnostics.
        """

        return {
            "version": self.version,
            "destructive": self.destructive,
            "requires_confirmation": (
                self.requires_confirmation
            ),
            "network_access": self.network_access,
            "filesystem_access": (
                self.filesystem_access
            ),
            "system_access": self.system_access,
            "safe": self.safe,
            "tags": sorted(
                self.tags,
            ),
            "attributes": dict(
                self.attributes,
            ),
        }