"""
Shell command execution tool.

Executes an operating system command and returns the result.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from backend.core.tools.context import ToolContext
from backend.core.tools.result import ToolResult
from backend.core.tools.tool import Tool


class ExecuteCommandTool(Tool):
    """
    Execute an operating system command.
    """

    def __init__(self) -> None:
        super().__init__(
            name="execute_command",
            description="Execute an operating system command.",
        )

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def execute(
        self,
        context: ToolContext,
    ) -> ToolResult:
        """
        Execute a shell command.
        """
        started_at = datetime.now(UTC)

        if context.is_cancelled:
            return ToolResult.failure(
                error="Tool execution was cancelled.",
                started_at=started_at,
            )

        command = context.argument("command")

        if not isinstance(command, str) or not command.strip():
            return ToolResult.failure(
                error="Missing required argument 'command'.",
                started_at=started_at,
            )

        cwd = context.argument("cwd")

        timeout = context.argument(
            "timeout",
            300,
        )

        try:
            process = await asyncio.create_subprocess_shell(
                command,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout,
            )

        except TimeoutError:
            return ToolResult.failure(
                error="Command execution timed out.",
                started_at=started_at,
            )

        except Exception as exc:
            return ToolResult.failure(
                error=str(exc),
                started_at=started_at,
            )

        stdout = stdout_bytes.decode(
            errors="replace",
        )

        stderr = stderr_bytes.decode(
            errors="replace",
        )

        return ToolResult.ok(
            output={
                "command": command,
                "exit_code": process.returncode,
                "stdout": stdout,
                "stderr": stderr,
            },
            started_at=started_at,
            metadata={
                "tool": self.name,
                "cwd": cwd,
            },
        )