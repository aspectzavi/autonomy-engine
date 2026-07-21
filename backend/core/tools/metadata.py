"""
Tool metadata.

Describes executable tools independently of their implementation.

Tool metadata is used for discovery, registration, diagnostics, and
future planner/LLM tool selection.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class ToolMetadata:
    """
    Immutable description of a tool.
    """

    name: str

    description: str

    category: str

    version: str = "1.0.0"

    tags: tuple[str, ...] = field(
        default_factory=tuple,
    )

    enabled: bool = True

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return metadata diagnostics.
        """
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "version": self.version,
            "tags": list(self.tags),
            "enabled": self.enabled,
        }