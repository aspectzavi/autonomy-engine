"""
Graph compiler.

Defines the interface responsible for compiling an optimized execution
graph into an executable workflow.

The graph compiler forms the bridge between the planning subsystem and
the workflow runtime.

Responsibilities:

- consume an ExecutionGraph
- construct a Workflow
- preserve dependency ordering
- preserve execution metadata

Concrete implementations may support deterministic compilation,
parallel scheduling, distributed execution, or adaptive workflows.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from backend.core.planning.execution_graph import (
    ExecutionGraph,
)
from backend.core.workflows.workflow import (
    Workflow,
)


class GraphCompiler(ABC):
    """
    Base interface for execution graph compilers.
    """

    @abstractmethod
    async def compile(
        self,
        graph: ExecutionGraph,
    ) -> Workflow:
        """
        Compile an execution graph into a workflow.

        Args:
            graph:
                Optimized execution graph.

        Returns:
            Executable workflow.
        """

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return compiler diagnostics.
        """

        return {
            "compiler": self.__class__.__name__,
        }