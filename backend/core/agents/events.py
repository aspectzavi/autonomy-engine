"""
Agent events.

Defines domain events emitted by autonomous agents.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


# ----------------------------------------------------------------------
# Base Event
# ----------------------------------------------------------------------


@dataclass(slots=True, frozen=True)
class AgentEvent:
    """
    Base class for all agent events.
    """

    agent: str

    occurred_at: datetime = field(
        default_factory=lambda: datetime.now(UTC),
        kw_only=True,
    )


# ----------------------------------------------------------------------
# Goal Events
# ----------------------------------------------------------------------


@dataclass(slots=True, frozen=True)
class GoalAccepted(AgentEvent):
    """
    Raised when an agent accepts a goal.
    """

    goal: str


@dataclass(slots=True, frozen=True)
class GoalCompleted(AgentEvent):
    """
    Raised when an agent successfully completes a goal.
    """

    goal: str


@dataclass(slots=True, frozen=True)
class GoalRejected(AgentEvent):
    """
    Raised when an agent rejects a goal.
    """

    goal: str

    reason: str


# ----------------------------------------------------------------------
# Lifecycle Events
# ----------------------------------------------------------------------


@dataclass(slots=True, frozen=True)
class AgentStarted(AgentEvent):
    """
    Raised when an agent begins execution.
    """

    goal: str


@dataclass(slots=True, frozen=True)
class AgentCompleted(AgentEvent):
    """
    Raised when an agent completes execution.
    """

    goal: str


@dataclass(slots=True, frozen=True)
class AgentFailed(AgentEvent):
    """
    Raised when an agent fails.
    """

    goal: str

    error: str