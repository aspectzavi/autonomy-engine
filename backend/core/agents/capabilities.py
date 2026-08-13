"""
Agent capabilities.

Defines the capabilities advertised by autonomous agents.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class AgentCapabilities:
    """
    Immutable collection of agent capabilities.
    """

    capabilities: frozenset[str] = field(
        default_factory=frozenset,
    )

    def supports(
        self,
        capability: str,
    ) -> bool:
        """
        Whether the capability is supported.
        """
        return capability in self.capabilities

    def supports_all(
        self,
        *capabilities: str,
    ) -> bool:
        """
        Whether all capabilities are supported.
        """
        return all(
            capability in self.capabilities
            for capability in capabilities
        )

    def supports_any(
        self,
        *capabilities: str,
    ) -> bool:
        """
        Whether any capability is supported.
        """
        return any(
            capability in self.capabilities
            for capability in capabilities
        )

    def add(
        self,
        *capabilities: str,
    ) -> "AgentCapabilities":
        """
        Return a new capability set with additional capabilities.
        """
        return AgentCapabilities(
            self.capabilities.union(capabilities),
        )

    def remove(
        self,
        *capabilities: str,
    ) -> "AgentCapabilities":
        """
        Return a new capability set with capabilities removed.
        """
        return AgentCapabilities(
            self.capabilities.difference(capabilities),
        )

    def intersection(
        self,
        other: "AgentCapabilities",
    ) -> "AgentCapabilities":
        """
        Return the shared capabilities.
        """
        return AgentCapabilities(
            self.capabilities.intersection(
                other.capabilities,
            ),
        )

    def union(
        self,
        other: "AgentCapabilities",
    ) -> "AgentCapabilities":
        """
        Return the union of both capability sets.
        """
        return AgentCapabilities(
            self.capabilities.union(
                other.capabilities,
            ),
        )

    def diagnostics(self) -> dict[str, object]:
        """
        Return capability diagnostics.
        """
        return {
            "count": len(self.capabilities),
            "capabilities": sorted(self.capabilities),
        }

    def __contains__(
        self,
        capability: object,
    ) -> bool:
        """
        Whether a capability exists.
        """
        return (
            isinstance(capability, str)
            and capability in self.capabilities
        )

    def __len__(self) -> int:
        """
        Number of supported capabilities.
        """
        return len(self.capabilities)

    def __iter__(self) -> Iterator[str]:
        """
        Iterate over capabilities.
        """
        return iter(sorted(self.capabilities))

    @classmethod
    def empty(cls) -> "AgentCapabilities":
        """
        Return an empty capability set.
        """
        return cls()

    @classmethod
    def of(
        cls,
        *capabilities: str,
    ) -> "AgentCapabilities":
        """
        Create a capability set.
        """
        return cls(
            frozenset(capabilities),
        )