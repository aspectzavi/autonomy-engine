"""
Tool executor tests.
"""

from __future__ import annotations

import pytest

from backend.core.tools.context import ToolContext
from backend.core.tools.executor import ToolExecutor
from backend.core.tools.manager import ToolManager
from backend.core.tools.registry import ToolRegistry
from backend.core.tools.result import ToolResult
from backend.core.tools.tool import Tool


class _EchoTool(Tool):
    def __init__(self) -> None:
        super().__init__(name="echo", description="Echoes input.")

    async def execute(self, context: ToolContext) -> ToolResult:
        return ToolResult.ok(output=context.argument("text"))


def test_executor_keeps_an_injected_empty_registry() -> None:
    """
    Regression test: ToolRegistry defines __len__, so an
    injected-but-empty registry is falsy. `registry or
    ToolRegistry()` silently discarded it, permanently pointing the
    executor at a different registry than the one tools get
    registered into.
    """

    registry = ToolRegistry()
    assert len(registry) == 0

    executor = ToolExecutor(registry)

    assert executor.registry is registry


@pytest.mark.asyncio
async def test_manager_executes_a_tool_registered_after_construction() -> None:
    """
    The real-world shape of the bug: ToolManager is constructed
    first (registry empty), tools are registered later by
    ToolService.on_start(). Execution must still find them.
    """

    manager = ToolManager()
    manager.register(_EchoTool())

    result = await manager.execute(
        tool="echo",
        context=ToolContext(arguments={"text": "hello"}),
    )

    assert result.success
    assert result.output == "hello"


def test_manager_shares_one_registry_with_its_executor() -> None:
    manager = ToolManager()

    assert manager.executor.registry is manager.registry
