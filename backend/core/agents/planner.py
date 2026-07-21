"""
Agent planner.

Defines the interface for translating high-level goals into executable
workflows.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from backend.core.agents.goal import Goal
from backend.core.workflows.workflow import Workflow


class AgentPlanner(ABC):
    """
    Base class for agent planners.
    An agent planner is responsible for translating a high-level goal
    into an executable workflow.

    Implementations may use:
    - rule-based planning
    - LLM reasoning
    - graph search
    - hierarchical task decomposition
    - multi-agent delegation

    The resulting workflow is then executed by the workflow subsystem.
    """

    @abstractmethod
    async def plan(
        self,
        goal: Goal,
    ) -> Workflow:
        """
        Produce an executable workflow.
        """
        raise NotImplementedError