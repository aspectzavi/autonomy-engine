"""
Example echo workflow.

Demonstrates execution of a ToolTask using the EchoTool.
"""

from __future__ import annotations

from backend.core.tasks.tool_task import ToolTask
from backend.core.tools.context import ToolContext
from backend.core.tools.manager import ToolManager
from backend.core.workflows.workflow import Workflow
from backend.tools.factory import BuiltinToolFactory


class EchoWorkflow(Workflow):
    """
    Simple workflow that executes the EchoTool.
    """

    def __init__(
        self,
        *,
        message: str,
    ) -> None:
        super().__init__(
            name="echo-workflow",
        )

        tool_manager = ToolManager()

        BuiltinToolFactory().register_all(
            tool_manager,
        )

        task = ToolTask(
            name="echo",
            tool="echo",
            tool_manager=tool_manager,
            tool_context=ToolContext(
                arguments={
                    "message": message,
                },
            ),
        )

        self.add_task(
            "echo",
            task,
        )

        self.validate()