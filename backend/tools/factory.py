"""
Built-in tool factory.

Creates and registers the framework's built-in tools.
"""

from __future__ import annotations

from backend.core.tools.manager import ToolManager
from backend.tools.shell.echo_tool import EchoTool
from backend.tools.shell.execute_command_tool import (
    ExecuteCommandTool,
)
from backend.tools.filesystem.read_file_tool import (
    ReadFileTool,
)


class BuiltinToolFactory:
    """
    Factory responsible for registering built-in tools.
    """

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register_all(
        self,
        manager: ToolManager,
    ) -> None:
        """
        Register all built-in tools.
        """

        manager.register(
            EchoTool(),
        )

        manager.register(
            ExecuteCommandTool(),
        )

        manager.register(
            ReadFileTool(),
        )

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
            "tools": [
                EchoTool.__name__,
                ExecuteCommandTool.__name__,
                ReadFileTool.__name__,
            ],
        }