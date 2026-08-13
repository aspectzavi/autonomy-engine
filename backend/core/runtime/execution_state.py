"""
Execution state.

Defines the lifecycle states of an autonomous runtime execution
session.

An execution represents the complete processing of a user request,
from planning through workflow execution to completion.
"""

from __future__ import annotations

from enum import Enum


class ExecutionState(str, Enum):
    """
    Runtime execution lifecycle.
    """

    CREATED = "created"

    PLANNING = "planning"

    DISPATCHING = "dispatching"

    EXECUTING = "executing"

    COMPLETED = "completed"

    FAILED = "failed"

    CANCELLED = "cancelled"

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_active(
        self,
    ) -> bool:
        """
        Whether execution is currently active.
        """
        return self in {
            ExecutionState.PLANNING,
            ExecutionState.DISPATCHING,
            ExecutionState.EXECUTING,
        }

    @property
    def is_terminal(
        self,
    ) -> bool:
        """
        Whether execution has reached a terminal state.
        """
        return self in {
            ExecutionState.COMPLETED,
            ExecutionState.FAILED,
            ExecutionState.CANCELLED,
        }

    @property
    def can_transition(
        self,
    ) -> bool:
        """
        Whether execution may transition to another state.
        """
        return not self.is_terminal

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return execution state diagnostics.
        """
        return {
            "state": self.value,
            "active": self.is_active,
            "terminal": self.is_terminal,
            "can_transition": self.can_transition,
        }