"""
Tool registry.

Stores and resolves executable tools by name.
"""

from __future__ import annotations

from collections.abc import Iterator

from backend.core.tools.exceptions import (
    ToolAlreadyRegisteredError,
    ToolNotFoundError,
)
from backend.core.tools.tool import Tool


class ToolRegistry:
    """
    Registry of executable tools.

    Provides registration and lookup functionality without managing
    execution or lifecycle.
    """

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        tool: Tool,
    ) -> None:
        """
        Register a tool.

        Raises:
            ToolAlreadyRegisteredError:
                If a tool with the same name already exists.
        """
        if tool.name in self._tools:
            raise ToolAlreadyRegisteredError(
                f"Tool '{tool.name}' is already registered."
            )

        self._tools[tool.name] = tool

    def unregister(
        self,
        name: str,
    ) -> Tool:
        """
        Remove and return a registered tool.

        Raises:
            ToolNotFoundError:
                If the tool is not registered.
        """
        try:
            return self._tools.pop(name)
        except KeyError as exc:
            raise ToolNotFoundError(
                f"Tool '{name}' is not registered."
            ) from exc

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get(
        self,
        name: str,
    ) -> Tool:
        """
        Return a registered tool.

        Raises:
            ToolNotFoundError:
                If the tool is not registered.
        """
        try:
            return self._tools[name]
        except KeyError as exc:
            raise ToolNotFoundError(
                f"Tool '{name}' is not registered."
            ) from exc

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Whether a tool is registered.
        """
        return name in self._tools

    # ------------------------------------------------------------------
    # Collection
    # ------------------------------------------------------------------

    def clear(
        self,
    ) -> None:
        """
        Remove all registered tools.
        """
        self._tools.clear()

    def values(
        self,
    ) -> tuple[Tool, ...]:
        """
        Return all registered tools.
        """
        return tuple(self._tools.values())

    # ------------------------------------------------------------------
    # Iteration
    # ------------------------------------------------------------------

    def __iter__(
        self,
    ) -> Iterator[Tool]:
        """
        Iterate over registered tools.
        """
        return iter(self._tools.values())

    def __len__(
        self,
    ) -> int:
        """
        Return the number of registered tools.
        """
        return len(self._tools)

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return registry diagnostics.
        """
        return {
            "tool_count": len(self),
            "tools": [
                tool.diagnostics()
                for tool in self
            ],
        }