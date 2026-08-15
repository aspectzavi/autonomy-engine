"""
Task service tests.
"""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from backend.core.observability.events import EventBus
from backend.core.observability.logger import KernelLogger
from backend.core.tasks.context import TaskContext
from backend.core.tasks.placeholder_task import PlaceholderTask
from backend.core.services.task_service import TaskService


def _context() -> TaskContext:
    return TaskContext(
        runtime=Mock(),
        container=Mock(),
        logger=KernelLogger(),
        events=EventBus(),
    )


def test_submit_returns_self_for_chaining() -> None:
    service = TaskService()

    result = service.submit(
        PlaceholderTask(capability="a", name="a"),
    )

    assert result is service
    assert len(service.queue) == 1


@pytest.mark.asyncio
async def test_run_all_executes_queued_tasks() -> None:
    service = TaskService()

    service.submit(PlaceholderTask(capability="a", name="a"))
    service.submit(PlaceholderTask(capability="b", name="b"))

    results = await service.run_all(_context())

    assert len(results) == 2
    assert all(result.success for result in results)
    assert service.queue.empty


@pytest.mark.asyncio
async def test_on_start_and_on_stop_lifecycle() -> None:
    service = TaskService()
    service.submit(PlaceholderTask(capability="a", name="a"))

    await service.start()

    assert service.is_running

    await service.stop()

    assert not service.is_running
    #
    # on_stop() clears the queue.
    #
    assert service.queue.empty


def test_diagnostics_include_pipeline() -> None:
    service = TaskService()

    diagnostics = service.diagnostics()

    assert "pipeline" in diagnostics
