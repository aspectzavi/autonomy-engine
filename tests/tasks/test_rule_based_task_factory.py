"""
Rule-based task factory tests.

Verifies the factory resolves capabilities to real ToolTasks when a
ToolManager holding that tool is available, and falls back to
PlaceholderTask otherwise.
"""

from __future__ import annotations

from backend.core.tasks.placeholder_task import PlaceholderTask
from backend.core.tasks.rule_based_task_factory import (
    RuleBasedTaskFactory,
)
from backend.core.tasks.tool_task import ToolTask
from backend.core.tools.context import ToolContext
from backend.core.tools.manager import ToolManager
from backend.core.tools.result import ToolResult
from backend.core.tools.tool import Tool


class _EchoTool(Tool):
    def __init__(self, name: str = "echo") -> None:
        super().__init__(name=name, description="Echoes its input.")

    async def execute(self, context: ToolContext) -> ToolResult:
        return ToolResult.ok(output=context.argument("text"))


def _manager_with(*tools: Tool) -> ToolManager:
    manager = ToolManager()
    for tool in tools:
        manager.register(tool)
    return manager


def test_falls_back_to_placeholder_without_a_tool_manager() -> None:
    factory = RuleBasedTaskFactory()

    task = factory.create(capability="echo")

    assert isinstance(task, PlaceholderTask)


def test_falls_back_to_placeholder_for_unknown_capability() -> None:
    factory = RuleBasedTaskFactory(
        tool_manager=_manager_with(_EchoTool()),
    )

    task = factory.create(capability="goal.execute")

    assert isinstance(task, PlaceholderTask)


def test_resolves_a_registered_tool_to_a_tool_task() -> None:
    manager = _manager_with(_EchoTool())
    factory = RuleBasedTaskFactory(tool_manager=manager)

    task = factory.create(capability="echo")

    assert isinstance(task, ToolTask)
    assert task.tool == "echo"
    assert task.tool_manager is manager


def test_tool_availability_is_checked_live_not_snapshotted() -> None:
    """
    Tools aren't registered into the manager until
    ToolService.on_start() runs, which can happen after this factory
    is constructed -- so availability must be re-checked on every
    create(), not captured once at construction time.
    """

    manager = _manager_with()
    factory = RuleBasedTaskFactory(tool_manager=manager)

    before = factory.create(capability="echo")
    assert isinstance(before, PlaceholderTask)

    manager.register(_EchoTool())

    after = factory.create(capability="echo")
    assert isinstance(after, ToolTask)


def test_custom_name_is_used() -> None:
    factory = RuleBasedTaskFactory(
        tool_manager=_manager_with(_EchoTool()),
    )

    task = factory.create(capability="echo", name="my-task")

    assert task.name == "my-task"


def test_name_defaults_to_the_capability() -> None:
    factory = RuleBasedTaskFactory()

    task = factory.create(capability="echo")

    assert task.name == "echo"


def test_diagnostics_report_tool_manager_attachment() -> None:
    without = RuleBasedTaskFactory()
    with_manager = RuleBasedTaskFactory(
        tool_manager=_manager_with(),
    )

    assert (
        without.diagnostics()["tool_manager_attached"] is False
    )
    assert (
        with_manager.diagnostics()["tool_manager_attached"] is True
    )
