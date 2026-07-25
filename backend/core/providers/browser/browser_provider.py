"""
Abstract browser provider.

Defines the contract for browser automation providers.

Concrete implementations may use:

- BrowserUse
- Playwright
- Chrome DevTools Protocol (CDP)
- Selenium
- Remote browser services

The remainder of the autonomy engine depends only on this abstraction.
"""

from __future__ import annotations

from abc import abstractmethod

from backend.core.providers.browser.browser_session import (
    BrowserSession,
)
from backend.core.providers.provider import Provider
from backend.core.providers.provider_result import (
    ProviderResult,
)


class BrowserProvider(Provider):
    """
    Base class for browser automation providers.
    """

    # ------------------------------------------------------------------
    # Browser Lifecycle
    # ------------------------------------------------------------------

    @abstractmethod
    async def start(
        self,
    ) -> None:
        """
        Start the browser provider.
        """

    @abstractmethod
    async def stop(
        self,
    ) -> None:
        """
        Stop the browser provider.
        """

    @property
    @abstractmethod
    def is_running(
        self,
    ) -> bool:
        """
        Whether the browser provider is running.
        """

    # ------------------------------------------------------------------
    # Session Management
    # ------------------------------------------------------------------

    @abstractmethod
    async def create_session(
        self,
    ) -> BrowserSession:
        """
        Create a browser session.
        """

    @abstractmethod
    async def close_session(
        self,
        session: BrowserSession,
    ) -> None:
        """
        Close a browser session.
        """

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    @abstractmethod
    async def navigate(
        self,
        session: BrowserSession,
        url: str,
    ) -> ProviderResult:
        """
        Navigate to a URL.
        """

    @abstractmethod
    async def back(
        self,
        session: BrowserSession,
    ) -> ProviderResult:
        """
        Navigate backward.
        """

    @abstractmethod
    async def forward(
        self,
        session: BrowserSession,
    ) -> ProviderResult:
        """
        Navigate forward.
        """

    @abstractmethod
    async def refresh(
        self,
        session: BrowserSession,
    ) -> ProviderResult:
        """
        Refresh the current page.
        """

    # ------------------------------------------------------------------
    # Interaction
    # ------------------------------------------------------------------

    @abstractmethod
    async def click(
        self,
        session: BrowserSession,
        selector: str,
    ) -> ProviderResult:
        """
        Click an element.
        """

    @abstractmethod
    async def type(
        self,
        session: BrowserSession,
        selector: str,
        text: str,
    ) -> ProviderResult:
        """
        Type into an element.
        """

    @abstractmethod
    async def press(
        self,
        session: BrowserSession,
        key: str,
    ) -> ProviderResult:
        """
        Press a keyboard key.
        """

    @abstractmethod
    async def scroll(
        self,
        session: BrowserSession,
        *,
        x: int = 0,
        y: int = 0,
    ) -> ProviderResult:
        """
        Scroll the page.
        """

    # ------------------------------------------------------------------
    # Information
    # ------------------------------------------------------------------

    @abstractmethod
    async def screenshot(
        self,
        session: BrowserSession,
    ) -> ProviderResult:
        """
        Capture a screenshot.
        """

    @abstractmethod
    async def content(
        self,
        session: BrowserSession,
    ) -> ProviderResult:
        """
        Retrieve the current page HTML.
        """

    @abstractmethod
    async def current_url(
        self,
        session: BrowserSession,
    ) -> ProviderResult:
        """
        Retrieve the current page URL.
        """

    @abstractmethod
    async def title(
        self,
        session: BrowserSession,
    ) -> ProviderResult:
        """
        Retrieve the current page title.
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
        Execute a browser capability.
        """