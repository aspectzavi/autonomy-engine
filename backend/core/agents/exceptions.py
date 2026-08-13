"""
Agent exceptions.

Defines the exception hierarchy for the autonomous agent subsystem.
"""

from __future__ import annotations


class AgentError(Exception):
    """
    Base exception for all agent-related errors.
    """


# ----------------------------------------------------------------------
# Registry
# ----------------------------------------------------------------------


class AgentRegistrationError(AgentError):
    """
    Base class for agent registration errors.
    """


class AgentAlreadyRegisteredError(AgentRegistrationError):
    """
    Raised when attempting to register an agent that already exists.
    """


class AgentNotFoundError(AgentRegistrationError):
    """
    Raised when a requested agent cannot be found.
    """


# ----------------------------------------------------------------------
# Execution
# ----------------------------------------------------------------------


class AgentExecutionError(AgentError):
    """
    Raised when agent execution fails.
    """


class GoalRejectedError(AgentExecutionError):
    """
    Raised when an agent rejects a goal.
    """


class AgentCancelledError(AgentExecutionError):
    """
    Raised when agent execution is cancelled.
    """


class AgentTimeoutError(AgentExecutionError):
    """
    Raised when agent execution exceeds the allowed time.
    """


# ----------------------------------------------------------------------
# Planning
# ----------------------------------------------------------------------


class PlanningError(AgentError):
    """
    Raised when workflow planning fails.
    """


# ----------------------------------------------------------------------
# Capability
# ----------------------------------------------------------------------


class CapabilityError(AgentError):
    """
    Base class for capability-related errors.
    """


class UnsupportedCapabilityError(CapabilityError):
    """
    Raised when an agent lacks a required capability.
    """


# ----------------------------------------------------------------------
# Memory
# ----------------------------------------------------------------------


class MemoryError(AgentError):
    """
    Base class for agent memory errors.
    """


class MemoryKeyNotFoundError(MemoryError):
    """
    Raised when a memory entry does not exist.
    """