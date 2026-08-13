"""
Agent lifecycle states.
"""

from __future__ import annotations

from enum import StrEnum


class AgentState(StrEnum):
    """
    Lifecycle states for autonomous agents.
    """

    IDLE = "idle"

    PLANNING = "planning"

    EXECUTING = "executing"

    WAITING = "waiting"

    COMPLETED = "completed"

    FAILED = "failed"

    STOPPED = "stopped"

    @property
    def is_terminal(self) -> bool:
        """
        Whether the agent has reached a terminal state.
        """
        return self in {
            AgentState.COMPLETED,
            AgentState.FAILED,
            AgentState.STOPPED,
        }

    @property
    def is_active(self) -> bool:
        """
        Whether the agent is actively processing work.
        """
        return self in {
            AgentState.PLANNING,
            AgentState.EXECUTING,
            AgentState.WAITING,
        }