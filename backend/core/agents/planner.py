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

from backend.core.agents.context import AgentContext
from backend.core.agents.goal import Goal
from backend.core.planning.execution_plan import (
    ExecutionPlan,
)

class AgentPlanner(ABC):

    @abstractmethod
    async def plan(
        self,
        goal: Goal,
        context: AgentContext,
    ) -> ExecutionPlan:
        """
        Produce an execution plan for the supplied goal.

        The context provides runtime information such as:

        - retrieved memories
        - execution variables
        - runtime services
        - execution session
        """