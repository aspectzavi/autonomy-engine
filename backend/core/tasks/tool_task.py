"""
Tool task.

Task implementation that executes a registered tool.
"""

from __future__ import annotations

from backend.core.tasks.task import Task
from backend.core.tasks.context import TaskContext
from backend.core.tools.context import ToolContext
from backend.core.tools.manager import ToolManager
from backend.core.tools.result import ToolResult


class ToolTask(Task):
    """
    Task that executes a registered tool.
    """

    def __init__(
        self,
        *,
        name: str,
        tool: str,
        tool_manager: ToolManager,
        tool_context: ToolContext | None = None,
    ) -> None:
        super().__init__(
            name=name,
        )

        self._tool = tool
        self._tool_manager = tool_manager
        self._tool_context = (
            tool_context
            or ToolContext()
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def tool(self) -> str:
        """
        Name of the tool to execute.
        """
        return self._tool

    @property
    def tool_manager(self) -> ToolManager:
        """
        Tool manager.
        """
        return self._tool_manager

    @property
    def tool_context(self) -> ToolContext:
        """
        Tool execution context.
        """
        return self._tool_context

    # ------------------------------------------------------------------
    # Task implementation
    # ------------------------------------------------------------------

    async def run(
        self,
        context: TaskContext,
    ) -> ToolResult:
        """
        Execute the configured tool.
        """

        return await self.tool_manager.execute(
            tool=self.tool,
            context=self.tool_context,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return task diagnostics.
        """
        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "tool": self.tool,
            }
        )

        return diagnostics