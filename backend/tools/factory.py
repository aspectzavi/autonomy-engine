"""
Built-in tool factory.

Creates and registers the framework's built-in tools.
"""

from __future__ import annotations

from backend.core.tools.manager import ToolManager
from backend.core.tools.tool import Tool
from backend.tools.filesystem.read_file_tool import (
    ReadFileTool,
)
from backend.tools.shell.echo_tool import EchoTool
from backend.tools.shell.execute_command_tool import (
    ExecuteCommandTool,
)


class BuiltinToolFactory:
    """
    Factory responsible for constructing and registering
    the framework's built-in tools.
    """

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def create_all(
        self,
    ) -> tuple[Tool, ...]:
        """
        Create all built-in tools.
        """
        return (
            EchoTool(),
            ExecuteCommandTool(),
            ReadFileTool(),
        )

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register_all(
        self,
        manager: ToolManager,
    ) -> None:
        """
        Register all built-in tools.

        Registration is idempotent. Tools that are already
        registered are skipped.
        """
        for tool in self.create_all():
            if not manager.contains(tool.name):
                manager.register(tool)

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return factory diagnostics.
        """
        return {
            "tool_count": len(self.create_all()),
            "tools": [
                tool.name
                for tool in self.create_all()
            ],
        }