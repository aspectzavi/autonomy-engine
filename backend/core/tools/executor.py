"""
Tool executor.

Resolves and executes registered tools.
"""

from __future__ import annotations

from backend.core.tools.context import ToolContext
from backend.core.tools.registry import ToolRegistry
from backend.core.tools.result import ToolResult


class ToolExecutor:
    """
    Executes registered tools.

    The executor is responsible only for resolving tools and delegating
    execution. It does not perform planning, retries, or orchestration.
    """

    def __init__(
        self,
        registry: ToolRegistry | None = None,
    ) -> None:
        self._registry = registry or ToolRegistry()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def registry(self) -> ToolRegistry:
        """
        Return the tool registry.
        """
        return self._registry

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
        selected = self.registry.get(
            tool,
        )

        return await selected.execute(
            context,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return executor diagnostics.
        """
        return {
            "registry": self.registry.diagnostics(),
        }