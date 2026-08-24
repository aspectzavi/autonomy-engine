"""
Tool capability provider.

Adapts the tool subsystem (ToolManager / ToolRegistry) to the
CapabilityProvider interface, so every registered tool becomes a
capability the planner can select and CapabilityFactory can compile
into an executable workflow step.

Capabilities are queried live from the tool registry rather than
snapshotted at construction time, since tools aren't registered until
ToolService.on_start() runs (after this provider is constructed).
CapabilityRegistry.register() does take one snapshot of
`.capabilities` at registration time, so this provider must be
registered (via ToolService.on_start(), after tools are registered)
rather than at construction time, for that snapshot to be accurate.
"""

from __future__ import annotations

from backend.core.capabilities.capability import Capability
from backend.core.capabilities.capability_provider import (
    CapabilityProvider,
)
from backend.core.capabilities.capability_result import (
    CapabilityResult,
)
from backend.core.tools.context import ToolContext
from backend.core.tools.exceptions import ToolNotFoundError
from backend.core.tools.manager import ToolManager


class ToolCapabilityProvider(CapabilityProvider):
    """
    Exposes every registered tool as a capability.
    """

    def __init__(
        self,
        *,
        tool_manager: ToolManager,
    ) -> None:
        self._tool_manager = tool_manager

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    @property
    def name(
        self,
    ) -> str:
        """
        Provider name.
        """

        return "tools"

    @property
    def capabilities(
        self,
    ) -> tuple[Capability, ...]:
        """
        One capability per currently registered tool.
        """

        return tuple(
            Capability(
                name=tool.name,
                description=tool.description,
            )
            for tool in self._tool_manager.registry
        )

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def execute(
        self,
        capability: str,
        *,
        arguments: dict[str, object] | None = None,
    ) -> CapabilityResult:
        """
        Execute a tool through the capability interface.
        """

        try:
            tool = self._tool_manager.registry.get(
                capability,
            )
        except ToolNotFoundError:
            return CapabilityResult.failure(
                f"Unknown tool capability: '{capability}'.",
            )

        context = ToolContext(
            arguments=arguments or {},
        )

        result = await tool.execute(context)

        if result.success:
            return CapabilityResult.ok(
                output=result.output,
                metadata=result.metadata,
            )

        return CapabilityResult.failure(
            result.error or "Tool execution failed.",
            metadata=result.metadata,
        )
