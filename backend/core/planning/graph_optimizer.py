"""
Graph optimizer.

Defines the interface responsible for optimizing execution graphs prior
to workflow compilation.

The optimizer operates purely on graph structure and never performs
workflow execution.

Future implementations may:

- eliminate redundant edges
- merge equivalent nodes
- expose parallel execution opportunities
- minimize graph depth
- perform critical-path analysis
- validate graph integrity
- annotate scheduling hints
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from backend.core.planning.execution_graph import (
    ExecutionGraph,
)


class GraphOptimizer(ABC):
    """
    Base interface for execution graph optimizers.
    """

    @abstractmethod
    async def optimize(
        self,
        graph: ExecutionGraph,
    ) -> ExecutionGraph:
        """
        Optimize an execution graph.

        Args:
            graph:
                Execution graph produced by the planning subsystem.

        Returns:
            An optimized execution graph.
        """

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return optimizer diagnostics.
        """

        return {
            "optimizer": self.__class__.__name__,
        }