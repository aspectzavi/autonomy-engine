"""
Selected capabilities.

Represents the immutable set of capabilities selected by the planning
subsystem for execution.

A SelectedCapabilities instance is produced by a CapabilitySelector and
consumed by a PlanningPolicy when constructing an ExecutionPlan.

The object intentionally contains no selection logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


@dataclass(
    frozen=True,
    slots=True,
)
class SelectedCapabilities:
    """
    Immutable collection of selected capabilities.
    """

    capabilities: tuple[str, ...] = field(
        default_factory=tuple,
    )

    metadata: dict[str, object] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def count(
        self,
    ) -> int:
        """
        Number of selected capabilities.
        """

        return len(
            self.capabilities,
        )

    @property
    def is_empty(
        self,
    ) -> bool:
        """
        Whether no capabilities were selected.
        """

        return self.count == 0

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def contains(
        self,
        capability: str,
    ) -> bool:
        """
        Determine whether a capability has been selected.
        """

        return capability in self.capabilities

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return selection diagnostics.
        """

        return {
            "count": self.count,
            "is_empty": self.is_empty,
            "capabilities": self.capabilities,
            "metadata": self.metadata,
        }