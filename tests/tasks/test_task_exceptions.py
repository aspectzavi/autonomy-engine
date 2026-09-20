"""
Task exception tests.

The important property here is backward compatibility:
EmptyTaskQueueError must subclass IndexError, because
TaskQueue.dequeue()/peek() and TaskScheduler.run_next() were
documented as raising IndexError and existing callers catch that.
"""

from __future__ import annotations

import pytest

from backend.core.tasks.exceptions import (
    EmptyTaskQueueError,
    TaskError,
    TaskQueueError,
)
from backend.core.tasks.queue import TaskQueue


def test_empty_queue_error_is_also_an_index_error() -> None:
    assert issubclass(EmptyTaskQueueError, IndexError)
    assert issubclass(EmptyTaskQueueError, TaskQueueError)
    assert issubclass(TaskQueueError, TaskError)


def test_dequeue_on_empty_queue_raises_specific_error() -> None:
    queue = TaskQueue()

    with pytest.raises(EmptyTaskQueueError):
        queue.dequeue()


def test_peek_on_empty_queue_raises_specific_error() -> None:
    queue = TaskQueue()

    with pytest.raises(EmptyTaskQueueError):
        queue.peek()


def test_existing_index_error_callers_still_work() -> None:
    """
    Regression guard: code written against the documented
    IndexError behavior must keep working unchanged.
    """

    queue = TaskQueue()

    with pytest.raises(IndexError):
        queue.dequeue()

    with pytest.raises(IndexError):
        queue.peek()
