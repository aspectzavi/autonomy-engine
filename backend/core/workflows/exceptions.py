"""
Workflow exceptions.

Defines the exception hierarchy used by the workflow engine.

The hierarchy intentionally distinguishes between validation,
construction, scheduling, execution, cancellation, and timeout
errors so callers can handle failures appropriately.
"""

from __future__ import annotations


class WorkflowError(Exception):
    """
    Base exception for all workflow-related failures.
    """


# ------------------------------------------------------------------
# Construction & Validation
# ------------------------------------------------------------------


class WorkflowValidationError(WorkflowError):
    """
    Raised when a workflow is structurally invalid.
    """


class WorkflowCycleError(WorkflowValidationError):
    """
    Raised when the workflow graph contains a cycle.
    """


class WorkflowNodeError(WorkflowValidationError):
    """
    Raised when an invalid workflow node is encountered.
    """


class WorkflowEdgeError(WorkflowValidationError):
    """
    Raised when an invalid workflow edge is encountered.
    """


class WorkflowDependencyError(WorkflowValidationError):
    """
    Raised when workflow dependencies are invalid.
    """


# ------------------------------------------------------------------
# Planning
# ------------------------------------------------------------------


class WorkflowPlanningError(WorkflowError):
    """
    Raised when workflow planning fails.
    """


# ------------------------------------------------------------------
# Scheduling
# ------------------------------------------------------------------


class WorkflowSchedulingError(WorkflowError):
    """
    Raised when workflow scheduling fails.
    """


# ------------------------------------------------------------------
# Execution
# ------------------------------------------------------------------


class WorkflowExecutionError(WorkflowError):
    """
    Raised when workflow execution fails.
    """


class WorkflowTaskError(WorkflowExecutionError):
    """
    Raised when a workflow task fails.
    """


class WorkflowCancelledError(WorkflowExecutionError):
    """
    Raised when workflow execution is cancelled.
    """


class WorkflowTimeoutError(WorkflowExecutionError):
    """
    Raised when workflow execution exceeds its timeout.
    """


class WorkflowCheckpointError(WorkflowExecutionError):
    """
    Raised when saving or restoring workflow checkpoints fails.
    """