"""
Plan optimizer.

Defines the interface responsible for optimizing execution plans before
they are compiled into workflows.

The optimizer operates after planning and before workflow compilation.

Responsibilities include:

- removing redundant steps
- merging compatible steps
- reordering independent steps
- inserting verification or checkpoint steps
- estimating execution characteristics
- producing an optimization report

Implementations are intentionally replaceable.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from backend.core.agents.context import AgentContext
from backend.core.planning.execution_plan import (
    ExecutionPlan,
)
from backend.core.planning.optimization_report import (
    OptimizationReport,
)


class PlanOptimizer(ABC):
    """
    Base interface for execution plan optimization.
    """

    @abstractmethod
    async def optimize(
        self,
        *,
        plan: ExecutionPlan,
        context: AgentContext,
    ) -> tuple[
        ExecutionPlan,
        OptimizationReport,
    ]:
        """
        Optimize an execution plan.

        Args:
            plan:
                Execution plan produced by the planner.

            context:
                Runtime execution context.

        Returns:
            A tuple containing:

            - optimized execution plan
            - optimization report
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