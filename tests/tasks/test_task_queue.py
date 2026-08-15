"""
Task queue tests.
"""

from __future__ import annotations

from backend.core.tasks.placeholder_task import PlaceholderTask
from backend.core.tasks.priority import TaskPriority
from backend.core.tasks.queue import TaskQueue


def _task(name: str, priority: TaskPriority = TaskPriority.NORMAL) -> PlaceholderTask:
    return PlaceholderTask(capability=name, name=name)


def test_queue_dequeues_by_priority_highest_first() -> None:
    queue = TaskQueue()

    low = PlaceholderTask(capability="low", name="low")
    low._priority = TaskPriority.LOW  # type: ignore[misc]

    high = PlaceholderTask(capability="high", name="high")
    high._priority = TaskPriority.CRITICAL  # type: ignore[misc]

    queue.enqueue(low)
    queue.enqueue(high)

    assert queue.dequeue() is high
    assert queue.dequeue() is low


def test_queue_preserves_fifo_for_equal_priority() -> None:
    queue = TaskQueue()

    first = _task("first")
    second = _task("second")

    queue.enqueue(first)
    queue.enqueue(second)

    assert queue.dequeue() is first
    assert queue.dequeue() is second


def test_queue_len_and_empty() -> None:
    queue = TaskQueue()

    assert queue.empty
    assert len(queue) == 0

    queue.enqueue(_task("a"))

    assert not queue.empty
    assert len(queue) == 1


def test_queue_clear() -> None:
    queue = TaskQueue()
    queue.enqueue(_task("a"))

    queue.clear()

    assert queue.empty
