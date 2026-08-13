"""
Tool base class.

Defines the base abstraction for executable tools.

A tool performs a single capability on behalf of an agent, such as
browser automation, file manipulation, HTTP requests, or shell
execution.

Tools should be stateless and reusable.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from backend.core.tools.context import ToolContext
from backend.core.tools.result import ToolResult


class Tool(ABC):
    """
    Base class for executable tools.

    A tool encapsulates a single capability that can be invoked by
    agents during workflow execution.
    """

    def __init__(
        self,
        *,
        name: str,
        description: str,
    ) -> None:
        self._name = name
        self._description = description

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        """
        Tool name.
        """
        return self._name

    @property
    def description(self) -> str:
        """
        Human-readable tool description.
        """
        return self._description

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    @abstractmethod
    async def execute(
        self,
        context: ToolContext,
    ) -> ToolResult:
        """
        Execute the tool.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return tool diagnostics.
        """
        return {
            "name": self.name,
            "description": self.description,
            "type": type(self).__name__,
        }