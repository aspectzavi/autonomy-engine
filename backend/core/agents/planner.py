"""
Agent planner.

Defines the interface for translating goals into execution plans.

Planning is intentionally separated from workflow compilation.
Implementations produce ExecutionPlan objects that are later compiled
into executable workflows.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from backend.core.agents.goal import Goal
from backend.core.planning.execution_plan import (
    ExecutionPlan,
)


class AgentPlanner(ABC):
    """
    Base interface for planners.
    """

    @abstractmethod
    async def plan(
        self,
        goal: Goal,
    ) -> ExecutionPlan:
        """
        Produce an execution plan.
        """