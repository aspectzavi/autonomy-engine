"""
Task exceptions.

Defines the exception hierarchy for the task subsystem.

Note on current usage: the task subsystem is deliberately
failure-tolerant at its edges -- Task.execute() catches exceptions
raised by run() and converts them into a failed TaskResult rather
than propagating, and TaskQueue.dequeue()/TaskScheduler.run_next()
raise the builtin IndexError on an empty queue. These types exist so
that callers and future implementations have a task-specific
hierarchy to raise and catch against (mirroring ToolError /
WorkflowError), rather than to replace those existing behaviors.
"""

from __future__ import annotations


class TaskError(Exception):
    """
    Base exception for all task-related errors.
    """


# ----------------------------------------------------------------------
# Queue
# ----------------------------------------------------------------------


class TaskQueueError(TaskError):
    """
    Base exception for task queue failures.
    """


class EmptyTaskQueueError(TaskQueueError, IndexError):
    """
    Raised when dequeuing from an empty queue.

    Also subclasses the builtin IndexError, so existing callers that
    catch IndexError (the documented behavior of TaskQueue.dequeue()
    and TaskScheduler.run_next()) keep working unchanged.
    """


# ----------------------------------------------------------------------
# Execution
# ----------------------------------------------------------------------


class TaskExecutionError(TaskError):
    """
    Raised when task execution fails.
    """


class TaskCancelledError(TaskExecutionError):
    """
    Raised when task execution is cancelled.
    """


class TaskTimeoutError(TaskExecutionError):
    """
    Raised when task execution exceeds its allowed timeout.
    """


class InvalidTaskContextError(TaskExecutionError):
    """
    Raised when a task receives an invalid execution context.
    """


# ----------------------------------------------------------------------
# Creation
# ----------------------------------------------------------------------


class TaskCreationError(TaskError):
    """
    Base exception for task creation failures.
    """


class UnknownCapabilityError(TaskCreationError):
    """
    Raised when a capability cannot be resolved to a task.
    """
