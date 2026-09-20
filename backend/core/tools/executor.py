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
        #
        # NOTE: must be `is None`, not `registry or ToolRegistry()`.
        # ToolRegistry defines __len__, so an injected-but-EMPTY
        # registry evaluates as falsy and would be silently replaced
        # by a new, disconnected one. This mattered in practice:
        # ToolManager correctly passes its own registry in here, but
        # that registry is always empty at construction time (tools
        # are only registered later, by ToolService.on_start()), so
        # `or` discarded it every single time. The executor ended up
        # permanently pointed at a different, forever-empty registry
        # than the one register() writes to -- meaning
        # ToolManager.execute() raised ToolNotFoundError for every
        # tool, even correctly registered ones. Same bug class
        # already fixed in AgentManager, ToolManager, and
        # TaskScheduler.
        #
        self._registry = (
            registry
            if registry is not None
            else ToolRegistry()
        )

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