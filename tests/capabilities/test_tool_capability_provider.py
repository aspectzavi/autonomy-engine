"""
Tool capability provider tests.
"""

from __future__ import annotations

import pytest

from backend.core.capabilities.tool_capability_provider import (
    ToolCapabilityProvider,
)
from backend.core.tools.context import ToolContext
from backend.core.tools.manager import ToolManager
from backend.core.tools.result import ToolResult
from backend.core.tools.tool import Tool


class _EchoTool(Tool):
    def __init__(self, name: str = "echo") -> None:
        super().__init__(name=name, description="Echoes its input.")

    async def execute(self, context: ToolContext) -> ToolResult:
        return ToolResult.ok(output=context.argument("text"))


class _FailingTool(Tool):
    def __init__(self) -> None:
        super().__init__(name="failing", description="Always fails.")

    async def execute(self, context: ToolContext) -> ToolResult:
        return ToolResult.failure(error="boom")


def _manager_with(*tools: Tool) -> ToolManager:
    manager = ToolManager()
    for tool in tools:
        manager.register(tool)
    return manager


def test_capabilities_reflect_registered_tools() -> None:
    manager = _manager_with(_EchoTool())
    provider = ToolCapabilityProvider(tool_manager=manager)

    names = [c.name for c in provider.capabilities]

    assert names == ["echo"]


def test_capabilities_are_queried_live_not_snapshotted() -> None:
    manager = _manager_with()
    provider = ToolCapabilityProvider(tool_manager=manager)

    assert provider.capabilities == ()

    manager.register(_EchoTool())

    assert len(provider.capabilities) == 1


@pytest.mark.asyncio
async def test_execute_delegates_to_the_matching_tool() -> None:
    manager = _manager_with(_EchoTool())
    provider = ToolCapabilityProvider(tool_manager=manager)

    result = await provider.execute(
        "echo",
        arguments={"text": "hello"},
    )

    assert result.success
    assert result.output == "hello"


@pytest.mark.asyncio
async def test_execute_reports_tool_failure_as_capability_failure() -> None:
    manager = _manager_with(_FailingTool())
    provider = ToolCapabilityProvider(tool_manager=manager)

    result = await provider.execute("failing")

    assert not result.success
    assert result.error == "boom"


@pytest.mark.asyncio
async def test_execute_unknown_capability_fails_cleanly() -> None:
    manager = _manager_with()
    provider = ToolCapabilityProvider(tool_manager=manager)

    result = await provider.execute("does-not-exist")

    assert not result.success
    assert "does-not-exist" in result.error


def test_provider_name() -> None:
    provider = ToolCapabilityProvider(tool_manager=ToolManager())

    assert provider.name == "tools"
