"""
Dependency analyzer.

Builds a dependency graph from an execution plan.

The analyzer is responsible for translating the ordered list of plan
steps into an explicit dependency graph.

The initial implementation assumes sequential execution:

    step1
      ↓
    step2
      ↓
    step3

Future implementations may infer:

- parallel execution
- synchronization barriers
- conditional branches
- resource conflicts
- dynamic dependencies
"""

from __future__ import annotations

from backend.core.planning.dependency_graph import (
    DependencyGraph,
)
from backend.core.planning.execution_plan import (
    ExecutionPlan,
)


class DependencyAnalyzer:
    """
    Builds dependency graphs from execution plans.
    """

    # ------------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------------

    def analyze(
        self,
        plan: ExecutionPlan,
    ) -> DependencyGraph:
        """
        Build a dependency graph for an execution plan.

        The current implementation assumes each step depends on the
        immediately preceding step.
        """

        if plan.is_empty:
            return DependencyGraph()

        dependencies: dict[str, tuple[str, ...]] = {}

        previous_step_id: str | None = None

        for step in plan.steps:
            if previous_step_id is None:
                dependencies[step.id] = ()
            else:
                dependencies[step.id] = (
                    previous_step_id,
                )

            previous_step_id = step.id

        return DependencyGraph(
            dependencies=dependencies,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return analyzer diagnostics.
        """

        return {
            "analyzer": self.__class__.__name__,
            "strategy": "sequential",
        }