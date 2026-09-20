"""
TaskService capability-resolution tests.

Covers the wiring added so a capability name can become a queued,
executable task -- including the end-to-end path where a real
registered tool actually runs through the task queue.
"""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from backend.core.observability.events import EventBus
from backend.core.observability.logger import KernelLogger
from backend.core.services.task_service import TaskService
from backend.core.services.tool_service import ToolService
from backend.core.tasks.context import TaskContext
from backend.core.tasks.placeholder_task import PlaceholderTask
from backend.core.tasks.tool_task import ToolTask
from backend.core.tools.context import ToolContext
from backend.core.tools.manager import ToolManager
from backend.core.tools.result import ToolResult
from backend.core.tools.tool import Tool


class _EchoTool(Tool):
    def __init__(self) -> None:
        super().__init__(name="echo", description="Echoes.")

    async def execute(self, context: ToolContext) -> ToolResult:
        return ToolResult.ok(output="echoed")


class _FailingTool(Tool):
    def __init__(self) -> None:
        super().__init__(name="failing", description="Fails.")

    async def execute(self, context: ToolContext) -> ToolResult:
        return ToolResult.failure(error="boom")


def _context() -> TaskContext:
    return TaskContext(
        runtime=Mock(),
        container=Mock(),
        logger=KernelLogger(),
        events=EventBus(),
    )


def _service_with(*tools: Tool) -> TaskService:
    manager = ToolManager()
    for tool in tools:
        manager.register(tool)

    return TaskService(
        tool_service=ToolService(manager=manager),
    )


def test_create_resolves_a_registered_tool() -> None:
    service = _service_with(_EchoTool())

    task = service.create(capability="echo")

    assert isinstance(task, ToolTask)


def test_create_falls_back_for_unknown_capability() -> None:
    service = _service_with(_EchoTool())

    task = service.create(capability="goal.execute")

    assert isinstance(task, PlaceholderTask)


def test_service_without_tool_service_still_works() -> None:
    service = TaskService()

    task = service.create(capability="echo")

    assert isinstance(task, PlaceholderTask)


def test_submit_capability_queues_the_task() -> None:
    service = _service_with(_EchoTool())

    returned = service.submit_capability("echo")

    assert returned is service
    assert len(service.queue) == 1


@pytest.mark.asyncio
async def test_real_tool_runs_end_to_end_through_the_queue() -> None:
    service = _service_with(_EchoTool())

    service.submit_capability("echo")

    results = await service.run_all(_context())

    assert len(results) == 1
    assert results[0].success
    assert service.queue.empty


@pytest.mark.asyncio
async def test_failing_tool_produces_a_failed_task_result() -> None:
    service = _service_with(_FailingTool())

    service.submit_capability("failing")

    results = await service.run_all(_context())

    assert len(results) == 1
    assert not results[0].success


@pytest.mark.asyncio
async def test_mixed_real_and_placeholder_capabilities() -> None:
    service = _service_with(_EchoTool())

    service.submit_capability("echo")
    service.submit_capability("goal.execute")

    results = await service.run_all(_context())

    assert len(results) == 2
    assert all(result.success for result in results)


def test_diagnostics_include_factory() -> None:
    service = _service_with(_EchoTool())

    diagnostics = service.diagnostics()

    assert "factory" in diagnostics
    assert (
        diagnostics["factory"]["tool_manager_attached"] is True
    )
