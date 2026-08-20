"""
Built-in tool factory.

Creates and registers the framework's built-in tools.
"""

from __future__ import annotations

from backend.core.config.config import EngineConfig
from backend.core.providers.browser.browser_config import (
    BrowserConfig,
)
from backend.core.providers.browser.browser_provider import (
    BrowserProvider,
)
from backend.core.providers.browser.browser_session_manager import (
    BrowserSessionManager,
)
from backend.core.providers.browser.playwright_browser_provider import (
    PlaywrightBrowserProvider,
)
from backend.core.providers.desktop.desktop_provider import (
    DesktopProvider,
)
from backend.core.providers.desktop.desktop_session_manager import (
    DesktopSessionManager,
)
from backend.core.providers.desktop.pywinauto_desktop_provider import (
    PywinautoDesktopProvider,
)
from backend.core.tools.manager import ToolManager
from backend.core.tools.tool import Tool
from backend.tools.browser.click_tool import ClickTool
from backend.tools.browser.download_tool import DownloadTool
from backend.tools.browser.extract_links_tool import (
    ExtractLinksTool,
)
from backend.tools.browser.extract_structured_tool import (
    ExtractStructuredTool,
)
from backend.tools.browser.extract_text_tool import (
    ExtractTextTool,
)
from backend.tools.browser.fill_tool import FillTool
from backend.tools.browser.navigate_tool import NavigateTool
from backend.tools.browser.press_key_tool import PressKeyTool
from backend.tools.browser.scrape_tool import ScrapeTool
from backend.tools.browser.screenshot_tool import (
    ScreenshotTool,
)
from backend.tools.browser.scroll_tool import ScrollTool
from backend.tools.browser.upload_file_tool import (
    UploadFileTool,
)
from backend.tools.browser.wait_tool import WaitTool
from backend.tools.desktop.click_at_tool import ClickAtTool
from backend.tools.desktop.click_element_tool import (
    ClickElementTool,
)
from backend.tools.desktop.connect_window_tool import (
    ConnectWindowTool,
)
from backend.tools.desktop.drag_tool import DragTool
from backend.tools.desktop.extract_structured_tool import (
    ExtractStructuredTool as DesktopExtractStructuredTool,
)
from backend.tools.desktop.get_element_text_tool import (
    GetElementTextTool,
)
from backend.tools.desktop.launch_app_tool import LaunchAppTool
from backend.tools.desktop.list_windows_tool import (
    ListWindowsTool,
)
from backend.tools.desktop.move_mouse_tool import MoveMouseTool
from backend.tools.desktop.press_key_tool import (
    PressKeyTool as DesktopPressKeyTool,
)
from backend.tools.desktop.screenshot_tool import (
    ScreenshotTool as DesktopScreenshotTool,
)
from backend.tools.desktop.scroll_at_tool import ScrollAtTool
from backend.tools.desktop.type_into_element_tool import (
    TypeIntoElementTool,
)
from backend.tools.desktop.type_text_tool import TypeTextTool
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
        desktop_provider: DesktopProvider | None = None,
        engine_config: EngineConfig | None = None,
    ) -> None:
        #
        # NOTE: `is None`, not `browser_provider or ...()`, kept
        # consistent with the __len__ falsy-empty-collection
        # discipline used throughout this codebase.
        #
        provider = browser_provider

        if provider is None:
            browser_config = (
                BrowserConfig.from_engine_config(
                    engine_config.browser,
                )
                if engine_config is not None
                else None
            )

            provider = PlaywrightBrowserProvider(
                config=browser_config,
            )

        self._browser_sessions = BrowserSessionManager(
            provider=provider,
        )

        self._desktop_sessions = DesktopSessionManager(
            provider=(
                desktop_provider
                if desktop_provider is not None
                else PywinautoDesktopProvider()
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
    # Desktop lifecycle
    # ------------------------------------------------------------------

    @property
    def desktop_sessions(
        self,
    ) -> DesktopSessionManager:
        """
        Shared desktop session manager used by every desktop tool.
        """

        return self._desktop_sessions

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
        desktop = self._desktop_sessions

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
            ExtractLinksTool(sessions=sessions),
            ExtractStructuredTool(sessions=sessions),
            ScrapeTool(sessions=sessions),
            ScreenshotTool(sessions=sessions),
            WaitTool(sessions=sessions),
            UploadFileTool(sessions=sessions),
            DownloadTool(sessions=sessions),
            ListWindowsTool(sessions=desktop),
            ConnectWindowTool(sessions=desktop),
            LaunchAppTool(sessions=desktop),
            ClickElementTool(sessions=desktop),
            TypeIntoElementTool(sessions=desktop),
            GetElementTextTool(sessions=desktop),
            DesktopExtractStructuredTool(sessions=desktop),
            ClickAtTool(sessions=desktop),
            MoveMouseTool(sessions=desktop),
            DragTool(sessions=desktop),
            ScrollAtTool(sessions=desktop),
            TypeTextTool(sessions=desktop),
            DesktopPressKeyTool(sessions=desktop),
            DesktopScreenshotTool(sessions=desktop),
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
