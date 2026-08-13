"""
Dependency graph.

Represents the dependency relationships between execution plan steps.

The dependency graph is produced by the DependencyAnalyzer and later
consumed by graph optimization and workflow compilation.

This module intentionally contains no graph construction or optimization
logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


@dataclass(
    frozen=True,
    slots=True,
)
class DependencyGraph:
    """
    Immutable dependency graph.
    """

    #
    # Mapping:
    #
    # step_id -> prerequisite step ids
    #
    dependencies: dict[str, tuple[str, ...]] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def node_count(
        self,
    ) -> int:
        """
        Number of nodes.
        """

        return len(
            self.dependencies,
        )

    @property
    def edge_count(
        self,
    ) -> int:
        """
        Number of dependency edges.
        """

        return sum(
            len(edges)
            for edges in self.dependencies.values()
        )

    @property
    def is_empty(
        self,
    ) -> bool:
        """
        Whether the graph is empty.
        """

        return self.node_count == 0

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def prerequisites(
        self,
        step_id: str,
    ) -> tuple[str, ...]:
        """
        Return prerequisite steps for a node.
        """

        return self.dependencies.get(
            step_id,
            (),
        )

    def contains(
        self,
        step_id: str,
    ) -> bool:
        """
        Determine whether a node exists.
        """

        return step_id in self.dependencies

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return dependency graph diagnostics.
        """

        return {
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "is_empty": self.is_empty,
        }