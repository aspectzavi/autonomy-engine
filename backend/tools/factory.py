"""
Built-in tool factory.

Creates and registers the framework's built-in tools.
"""

from __future__ import annotations

from backend.core.providers.browser.browser_provider import (
    BrowserProvider,
)
from backend.core.providers.browser.browser_session_manager import (
    BrowserSessionManager,
)
from backend.core.providers.browser.playwright_browser_provider import (
    PlaywrightBrowserProvider,
)
from backend.core.tools.manager import ToolManager
from backend.core.tools.tool import Tool
from backend.tools.browser.click_tool import ClickTool
from backend.tools.browser.download_tool import DownloadTool
from backend.tools.browser.extract_text_tool import (
    ExtractTextTool,
)
from backend.tools.browser.fill_tool import FillTool
from backend.tools.browser.navigate_tool import NavigateTool
from backend.tools.browser.press_key_tool import PressKeyTool
from backend.tools.browser.screenshot_tool import (
    ScreenshotTool,
)
from backend.tools.browser.scroll_tool import ScrollTool
from backend.tools.browser.upload_file_tool import (
    UploadFileTool,
)
from backend.tools.browser.wait_tool import WaitTool
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

    def __init__(
        self,
        *,
        browser_provider: BrowserProvider | None = None,
    ) -> None:
        #
        # NOTE: `is None`, not `browser_provider or ...()`, kept
        # consistent with the __len__ falsy-empty-collection
        # discipline used throughout this codebase.
        #
        self._browser_sessions = BrowserSessionManager(
            provider=(
                browser_provider
                if browser_provider is not None
                else PlaywrightBrowserProvider()
            ),
        )

    # ------------------------------------------------------------------
    # Browser lifecycle
    # ------------------------------------------------------------------

    @property
    def browser_sessions(
        self,
    ) -> BrowserSessionManager:
        """
        Shared browser session manager used by every browser tool.

        Exposed so the owning service can close the browser session
        (and stop the underlying provider) on shutdown -- without
        this, a launched browser process would be left running /
        garbage-collected uncleanly instead of closed properly.
        """

        return self._browser_sessions

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def create_all(
        self,
    ) -> tuple[Tool, ...]:
        """
        Create all built-in tools.
        """
        sessions = self._browser_sessions

        return (
            EchoTool(),
            ExecuteCommandTool(),
            ReadFileTool(),
            NavigateTool(sessions=sessions),
            ClickTool(sessions=sessions),
            FillTool(sessions=sessions),
            PressKeyTool(sessions=sessions),
            ScrollTool(sessions=sessions),
            ExtractTextTool(sessions=sessions),
            ScreenshotTool(sessions=sessions),
            WaitTool(sessions=sessions),
            UploadFileTool(sessions=sessions),
            DownloadTool(sessions=sessions),
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
