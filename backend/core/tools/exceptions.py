"""
Tool exceptions.

Defines the exception hierarchy for the tool subsystem.
"""

from __future__ import annotations


class ToolError(Exception):
    """
    Base exception for all tool-related errors.
    """


# ----------------------------------------------------------------------
# Registration
# ----------------------------------------------------------------------


class ToolRegistrationError(ToolError):
    """
    Base exception for tool registration failures.
    """


class ToolAlreadyRegisteredError(ToolRegistrationError):
    """
    Raised when attempting to register a tool that already exists.
    """


class ToolNotFoundError(ToolRegistrationError):
    """
    Raised when a requested tool cannot be found.
    """


# ----------------------------------------------------------------------
# Execution
# ----------------------------------------------------------------------


class ToolExecutionError(ToolError):
    """
    Raised when tool execution fails.
    """


class ToolCancelledError(ToolExecutionError):
    """
    Raised when tool execution is cancelled.
    """


class ToolTimeoutError(ToolExecutionError):
    """
    Raised when tool execution exceeds its allowed timeout.
    """


class InvalidToolContextError(ToolExecutionError):
    """
    Raised when a tool receives an invalid execution context.
    """


# ----------------------------------------------------------------------
# Capability
# ----------------------------------------------------------------------


class ToolCapabilityError(ToolError):
    """
    Raised when a required capability is unavailable.
    """


class UnsupportedToolError(ToolError):
    """
    Raised when a requested tool operation is unsupported.
    """