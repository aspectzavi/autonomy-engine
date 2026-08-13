"""
Execution graph.

Represents the executable directed graph produced after dependency
analysis.

The execution graph is intentionally immutable and independent of the
workflow runtime. Later stages (scheduler, executor, optimizer, etc.)
consume this graph to determine execution order and parallelism.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from backend.core.planning.plan_step import PlanStep


@dataclass(
    frozen=True,
    slots=True,
)
class ExecutionGraph:
    """
    Immutable executable graph.
    """

    steps: tuple[PlanStep, ...] = field(
        default_factory=tuple,
    )

    edges: tuple[tuple[str, str], ...] = field(
        default_factory=tuple,
    )

    metadata: dict[str, object] = field(
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
        Number of execution nodes.
        """

        return len(
            self.steps,
        )

    @property
    def edge_count(
        self,
    ) -> int:
        """
        Number of dependency edges.
        """

        return len(
            self.edges,
        )

    @property
    def is_empty(
        self,
    ) -> bool:
        """
        Whether the graph contains no nodes.
        """

        return self.node_count == 0

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def successors(
        self,
        step_id: str,
    ) -> tuple[str, ...]:
        """
        Return all immediate successors.
        """

        return tuple(
            target
            for source, target in self.edges
            if source == step_id
        )

    def predecessors(
        self,
        step_id: str,
    ) -> tuple[str, ...]:
        """
        Return all immediate predecessors.
        """

        return tuple(
            source
            for source, target in self.edges
            if target == step_id
        )

    def step(
        self,
        step_id: str,
    ) -> PlanStep:
        """
        Retrieve a step by identifier.
        """

        for step in self.steps:
            if step.id == step_id:
                return step

        raise KeyError(
            step_id,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return execution graph diagnostics.
        """

        return {
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "is_empty": self.is_empty,
            "edges": self.edges,
            "metadata": self.metadata,
        }