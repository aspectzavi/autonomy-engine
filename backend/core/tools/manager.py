"""
Tool manager.

Coordinates executable tools through the tool registry.
"""

from __future__ import annotations

from backend.core.tools.context import ToolContext
from backend.core.tools.executor import ToolExecutor
from backend.core.tools.registry import ToolRegistry
from backend.core.tools.result import ToolResult
from backend.core.tools.tool import Tool


class ToolManager:
    """
    Coordinates registered tools.

    The manager is responsible for registering tools, resolving them,
    and dispatching execution through the ToolExecutor.
    """

    def __init__(
        self,
        registry: ToolRegistry | None = None,
        executor: ToolExecutor | None = None,
    ) -> None:
        self._registry = registry or ToolRegistry()
        self._executor = executor or ToolExecutor(
            self._registry,
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def registry(self) -> ToolRegistry:
        """
        Return the managed tool registry.
        """
        return self._registry

    @property
    def executor(self) -> ToolExecutor:
        """
        Return the tool executor.
        """
        return self._executor

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        tool: Tool,
    ) -> None:
        """
        Register a tool.
        """
        self.registry.register(tool)

    def unregister(
        self,
        name: str,
    ) -> Tool:
        """
        Unregister a tool.
        """
        return self.registry.unregister(name)

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get(
        self,
        name: str,
    ) -> Tool:
        """
        Return a registered tool.
        """
        return self.registry.get(name)

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Whether a tool is registered.
        """
        return self.registry.contains(name)

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def execute(
        self,
        *,
        tool: str,
        context: ToolContext,
    ) -> ToolResult:
        """
        Execute a registered tool.
        """
        return await self.executor.execute(
            tool=tool,
            context=context,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return manager diagnostics.
        """
        return {
            "registered_tools": len(self.registry),
            "registry": self.registry.diagnostics(),
            "executor": self.executor.diagnostics(),
        }