"""
Abstract desktop provider.

Defines the contract for desktop automation providers: controlling
windows and applications running on the local machine, both through
structured UI element access (find a button/field by name, like a CSS
selector) and through raw coordinate-based mouse/keyboard control (for
apps with no accessible UI tree -- custom-rendered canvases, games,
some legacy software).

Concrete implementations may use:

- pywinauto (Windows UI Automation)
- PyAutoGUI (coordinate/image-based fallback)
- AppleScript / macOS Accessibility API
- AT-SPI (Linux)

The remainder of the autonomy engine depends only on this abstraction.
"""

from __future__ import annotations

from abc import abstractmethod

from backend.core.providers.desktop.desktop_session import (
    DesktopSession,
)
from backend.core.providers.provider import Provider
from backend.core.providers.provider_result import (
    ProviderResult,
)


class DesktopProvider(Provider):
    """
    Base class for desktop automation providers.
    """

    # ------------------------------------------------------------------
    # Provider Lifecycle
    # ------------------------------------------------------------------

    @abstractmethod
    async def start(
        self,
    ) -> None:
        """
        Start the desktop provider.
        """

    @abstractmethod
    async def stop(
        self,
    ) -> None:
        """
        Stop the desktop provider.
        """

    @property
    @abstractmethod
    def is_running(
        self,
    ) -> bool:
        """
        Whether the desktop provider is running.
        """

    # ------------------------------------------------------------------
    # Session Management
    # ------------------------------------------------------------------

    @abstractmethod
    async def create_session(
        self,
    ) -> DesktopSession:
        """
        Create a desktop session, not yet connected to any window.
        """

    @abstractmethod
    async def close_session(
        self,
        session: DesktopSession,
    ) -> None:
        """
        Close a desktop session.
        """

    # ------------------------------------------------------------------
    # Window / Application Management
    # ------------------------------------------------------------------

    @abstractmethod
    async def list_windows(
        self,
        session: DesktopSession,
    ) -> ProviderResult:
        """
        List currently open top-level windows.

        Output is a list of dicts with `title`, `process_id`, and
        `class_name`.
        """

    @abstractmethod
    async def connect_window(
        self,
        session: DesktopSession,
        *,
        title: str | None = None,
        title_pattern: str | None = None,
        process_id: int | None = None,
    ) -> ProviderResult:
        """
        Connect the session to an already-open window, matched by
        exact title, a title regex pattern, or process ID.
        """

    @abstractmethod
    async def launch(
        self,
        session: DesktopSession,
        path: str,
        *,
        arguments: tuple[str, ...] = (),
    ) -> ProviderResult:
        """
        Launch a new process and connect the session to its window.
        """

    # ------------------------------------------------------------------
    # Structured element interaction (works when the target app
    # exposes a UI Automation tree -- most native Windows apps)
    # ------------------------------------------------------------------

    @abstractmethod
    async def click_element(
        self,
        session: DesktopSession,
        *,
        name: str | None = None,
        automation_id: str | None = None,
        control_type: str | None = None,
    ) -> ProviderResult:
        """
        Click an element in the connected window, matched by name,
        automation ID, and/or control type (at least one required).
        """

    @abstractmethod
    async def type_into_element(
        self,
        session: DesktopSession,
        text: str,
        *,
        name: str | None = None,
        automation_id: str | None = None,
        control_type: str | None = None,
    ) -> ProviderResult:
        """
        Click an element and type text into it.
        """

    @abstractmethod
    async def get_element_text(
        self,
        session: DesktopSession,
        *,
        name: str | None = None,
        automation_id: str | None = None,
        control_type: str | None = None,
    ) -> ProviderResult:
        """
        Retrieve the text of an element.
        """

    @abstractmethod
    async def extract_structured(
        self,
        session: DesktopSession,
    ) -> ProviderResult:
        """
        Extract a generic structured summary of the connected
        window's UI tree: every control's type, name, automation ID,
        and bounding rectangle.

        Works on any app that exposes a UI Automation tree, without
        needing to know its layout ahead of time -- the desktop
        equivalent of extract_structured() on BrowserProvider.
        """

    # ------------------------------------------------------------------
    # Coordinate-based fallback (works on anything on screen,
    # regardless of whether it exposes a UI Automation tree)
    # ------------------------------------------------------------------

    @abstractmethod
    async def click_at(
        self,
        session: DesktopSession,
        x: int,
        y: int,
        *,
        button: str = "left",
        clicks: int = 1,
    ) -> ProviderResult:
        """
        Click at absolute screen coordinates.
        """

    @abstractmethod
    async def move_to(
        self,
        session: DesktopSession,
        x: int,
        y: int,
    ) -> ProviderResult:
        """
        Move the mouse to absolute screen coordinates.
        """

    @abstractmethod
    async def drag(
        self,
        session: DesktopSession,
        *,
        from_x: int,
        from_y: int,
        to_x: int,
        to_y: int,
    ) -> ProviderResult:
        """
        Drag the mouse from one point to another.
        """

    @abstractmethod
    async def scroll_at(
        self,
        session: DesktopSession,
        x: int,
        y: int,
        amount: int,
    ) -> ProviderResult:
        """
        Scroll at a screen position. Positive `amount` scrolls up.
        """

    # ------------------------------------------------------------------
    # Keyboard (global, not tied to a specific element)
    # ------------------------------------------------------------------

    @abstractmethod
    async def type_text(
        self,
        session: DesktopSession,
        text: str,
    ) -> ProviderResult:
        """
        Type text at the current keyboard focus.
        """

    @abstractmethod
    async def press_key(
        self,
        session: DesktopSession,
        key: str,
    ) -> ProviderResult:
        """
        Press a key or key combination (e.g. "enter", "ctrl+c").
        """

    # ------------------------------------------------------------------
    # Information
    # ------------------------------------------------------------------

    @abstractmethod
    async def screenshot(
        self,
        session: DesktopSession,
    ) -> ProviderResult:
        """
        Capture a screenshot: the connected window's region if a
        window is connected, otherwise the full screen.
        """

    @abstractmethod
    async def current_window_title(
        self,
        session: DesktopSession,
    ) -> ProviderResult:
        """
        Retrieve the connected window's current title.
        """

    # ------------------------------------------------------------------
    # Provider Interface
    # ------------------------------------------------------------------

    @abstractmethod
    async def execute(
        self,
        capability: str,
        *,
        arguments: dict[str, object] | None = None,
    ) -> ProviderResult:
        """
        Execute a desktop capability.
        """
