"""
Tool capabilities.

Defines the capabilities advertised by executable tools.

Capabilities are used for discovery, planning, diagnostics, and future
tool selection by autonomous agents.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# ----------------------------------------------------------------------
# Capability
# ----------------------------------------------------------------------


@dataclass(slots=True, frozen=True)
class ToolCapability:
    """
    Immutable tool capability.
    """

    name: str

    description: str


# ----------------------------------------------------------------------
# Capability Collection
# ----------------------------------------------------------------------


@dataclass(slots=True, frozen=True)
class ToolCapabilities:
    """
    Collection of tool capabilities.
    """

    capabilities: tuple[
        ToolCapability,
        ...,
    ] = field(
        default_factory=tuple,
    )

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Whether the capability exists.
        """
        return any(
            capability.name == name
            for capability in self.capabilities
        )

    def names(
        self,
    ) -> tuple[str, ...]:
        """
        Return capability names.
        """
        return tuple(
            capability.name
            for capability in self.capabilities
        )

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return capability diagnostics.
        """
        return {
            "count": len(self.capabilities),
            "capabilities": [
                {
                    "name": capability.name,
                    "description": capability.description,
                }
                for capability in self.capabilities
            ],
        }


# ----------------------------------------------------------------------
# Common Capabilities
# ----------------------------------------------------------------------

BROWSER_NAVIGATION = ToolCapability(
    name="browser.navigation",
    description="Navigate browser pages.",
)

BROWSER_DOM = ToolCapability(
    name="browser.dom",
    description="Interact with DOM elements.",
)

BROWSER_SCREENSHOT = ToolCapability(
    name="browser.screenshot",
    description="Capture browser screenshots.",
)

FILESYSTEM_READ = ToolCapability(
    name="filesystem.read",
    description="Read files from storage.",
)

FILESYSTEM_WRITE = ToolCapability(
    name="filesystem.write",
    description="Write files to storage.",
)

SHELL_EXECUTE = ToolCapability(
    name="shell.execute",
    description="Execute shell commands.",
)

HTTP_REQUEST = ToolCapability(
    name="http.request",
    description="Perform HTTP requests.",
)

PYTHON_EXECUTE = ToolCapability(
    name="python.execute",
    description="Execute Python code.",
)