"""
Task scheduler tests.
"""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from backend.core.observability.events import EventBus
from backend.core.observability.logger import KernelLogger
from backend.core.tasks.context import TaskContext
from backend.core.tasks.placeholder_task import PlaceholderTask
from backend.core.tasks.queue import TaskQueue
from backend.core.tasks.scheduler import TaskScheduler


def _context() -> TaskContext:
    return TaskContext(
        runtime=Mock(),
        container=Mock(),
        logger=KernelLogger(),
        events=EventBus(),
    )


def test_scheduler_keeps_the_injected_queue_even_when_empty() -> None:
    """
    Regression test: TaskScheduler must keep an injected TaskQueue
    even when it is empty (same __len__ falsy-empty-collection bug
    class fixed in AgentManager and ToolManager).
    """

    queue = TaskQueue()
    assert len(queue) == 0

    scheduler = TaskScheduler(queue=queue)

    assert scheduler.queue is queue


@pytest.mark.asyncio
async def test_submit_and_run_next() -> None:
    scheduler = TaskScheduler()
    task = PlaceholderTask(capability="test", name="test")

    scheduler.submit(task)

    result = await scheduler.run_next(_context())

    assert result.success
    assert scheduler.queue.empty


@pytest.mark.asyncio
async def test_run_all_executes_every_queued_task() -> None:
    scheduler = TaskScheduler()

    for i in range(3):
        scheduler.submit(
            PlaceholderTask(capability=f"cap-{i}", name=f"task-{i}"),
        )

    results = await scheduler.run_all(_context())

    assert len(results) == 3
    assert all(result.success for result in results)
    assert scheduler.queue.empty
