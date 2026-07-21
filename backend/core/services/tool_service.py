"""
Tool service.

Runtime-managed service responsible for the executable tool subsystem.
"""

from __future__ import annotations

from backend.core.kernel.metadata import ServiceMetadata
from backend.core.kernel.service import KernelService
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
        Register built-in tools.
        """
        self.factory.register_all(
            self.manager,
        )

        self.logger.info(
            "Registered %d tools.",
            len(self.registry),
        )

    async def on_stop(self) -> None:
        """
        Shutdown the tool subsystem.
        """
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