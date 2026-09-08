"""
Tool service.

Runtime-managed service responsible for the executable tool subsystem.
"""

from __future__ import annotations

from backend.core.kernel.metadata import ServiceMetadata
from backend.core.kernel.service import KernelService
from backend.core.capabilities.capability_registry import (
    CapabilityRegistry,
)
from backend.core.capabilities.tool_capability_provider import (
    ToolCapabilityProvider,
)
from backend.core.tools.executor import ToolExecutor
from backend.core.tools.manager import ToolManager
from backend.core.tools.registry import ToolRegistry
from backend.tools.factory import BuiltinToolFactory


class ToolService(KernelService):
    """
    Runtime-managed tool subsystem.
    """

    def __init__(
        self,
        *,
        manager: ToolManager | None = None,
        factory: BuiltinToolFactory | None = None,
        capability_registry: CapabilityRegistry | None = None,
    ) -> None:
        super().__init__(
            metadata=ServiceMetadata(
                name="tool-service",
                version="1.0.0",
                description=(
                    "Runtime-managed tool subsystem."
                ),
            ),
        )

        self._manager = manager or ToolManager()
        self._factory = (
            factory
            or BuiltinToolFactory()
        )
        self._capability_registry = (
            capability_registry
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def manager(self) -> ToolManager:
        """
        Tool manager.
        """
        return self._manager

    @property
    def registry(self) -> ToolRegistry:
        """
        Tool registry.
        """
        return self.manager.registry

    @property
    def executor(self) -> ToolExecutor:
        """
        Tool executor.
        """
        return self.manager.executor

    @property
    def factory(self) -> BuiltinToolFactory:
        """
        Built-in tool factory.
        """
        return self._factory

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def on_start(self) -> None:
        """
        Register built-in tools, and expose them as capabilities.

        Registration into CapabilityRegistry happens here, after
        tools are registered, rather than at construction time --
        CapabilityRegistry.register() snapshots `provider.
        capabilities` once, and no tool exists yet when ToolService
        is constructed (they're only added by register_all() below).
        Guarded by name so restarting the runtime doesn't attempt a
        duplicate registration.
        """
        self.factory.register_all(
            self.manager,
        )

        self.logger.info(
            "Registered %d tools.",
            len(self.registry),
        )

        if self._capability_registry is not None:
            provider_names = {
                provider.name
                for provider in (
                    self._capability_registry.providers
                )
            }

            if "tools" not in provider_names:
                self._capability_registry.register(
                    ToolCapabilityProvider(
                        tool_manager=self.manager,
                    ),
                )

    async def on_stop(self) -> None:
        """
        Shutdown the tool subsystem.

        Closes the shared browser session and stops its provider,
        and closes the shared desktop session and stops its provider
        (if either was ever opened), then clears the tool registry.
        Without this, a launched browser process is left to be
        garbage collected uncleanly instead of shut down properly.
        """
        await self.factory.browser_sessions.close()
        await self.factory.browser_sessions.provider.stop()

        await self.factory.desktop_sessions.close()
        await self.factory.desktop_sessions.provider.stop()

        self.registry.clear()

        self.logger.info(
            "Tool registry cleared.",
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(self) -> dict[str, object]:
        """
        Return tool service diagnostics.
        """
        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "manager": (
                    self.manager.diagnostics()
                ),
                "factory": (
                    self.factory.diagnostics()
                ),
            }
        )

        return diagnostics