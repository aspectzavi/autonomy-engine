"""
BrowserUse provider.

Concrete browser provider backed by BrowserUse.

This initial implementation establishes lifecycle and session
management. Browser automation methods will be implemented
incrementally in later iterations.
"""

from __future__ import annotations
from typing import cast

from backend.core.providers.browser.browser_config import (
    BrowserConfig,
)
from backend.core.providers.browser.browser_provider import (
    BrowserProvider,
)
from backend.core.providers.browser.browser_session import (
    BrowserSession,
)
from backend.core.providers.provider_metadata import (
    ProviderMetadata,
)
from backend.core.providers.provider_result import (
    ProviderResult,
)
from backend.core.providers.browser.browser_use_adapter import (
    BrowserUseAdapter,
)


class BrowserUseProvider(BrowserProvider):
    """
    Browser provider backed by BrowserUse.
    """

    def __init__(
        self,
        *,
        config: BrowserConfig | None = None,
    ) -> None:
        super().__init__(
            ProviderMetadata(
                name="browser-use",
                version="0.1.0",
                description=(
                    "BrowserUse browser automation provider."
                ),
            ),
        )

        self._config = config or BrowserConfig()

        self._adapter = BrowserUseAdapter(
            config=self._config,
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def config(
        self,
    ) -> BrowserConfig:
        """
        Browser configuration.
        """

        return self._config

    @property
    def is_running(
        self,
    ) -> bool:
        """
        Whether the provider is running.
        """

        return self.adapter.is_running

    @property
    def adapter(
        self,
    ) -> BrowserUseAdapter:
        """
        BrowserUse adapter.
        """

        return self._adapter

    # ------------------------------------------------------------------
    # Provider
    # ------------------------------------------------------------------

    def supports(
        self,
        capability: str,
    ) -> bool:
        """
        Determine whether this provider supports a capability.
        """

        return capability.startswith(
            "browser."
        )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(
        self,
    ) -> None:
        """
        Start the provider.
        """

        await self.adapter.start()

    async def stop(
        self,
    ) -> None:
        """
        Stop the provider.
        """

        await self.adapter.stop()

    # ------------------------------------------------------------------
    # Sessions
    # ------------------------------------------------------------------

    async def create_session(
        self,
    ) -> BrowserSession:
        """
        Create a browser session.
        """

        return await self.adapter.create_session()

    async def close_session(
        self,
        session: BrowserSession,
    ) -> None:
        """
        Close a browser session.
        """

        await self.adapter.close_session(
            session,
        )

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    async def navigate(
        self,
        session: BrowserSession,
        url: str,
    ) -> ProviderResult:
        """
        Navigate to a URL.
        """

        if not self.is_running:
            return ProviderResult.failure(
                "Browser provider is not running.",
            )

        if not session.is_active:
            return ProviderResult.failure(
                "Browser session is closed.",
            )

        await self.adapter.navigate(
            session,
            url,
        )

        return ProviderResult.ok(
            output={
                "url": session.current_url,
                "title": session.current_title,
            },
        )

    async def back(
        self,
        session: BrowserSession,
    ) -> ProviderResult:
        """
        Navigate backward.

        Browser history will be implemented later.
        """

        if not self.is_running:
            return ProviderResult.failure(
                "Browser provider is not running.",
            )

        if not session.is_active:
            return ProviderResult.failure(
                "Browser session is closed.",
            )

        await self.adapter.back(
            session,
        )

        return ProviderResult.ok(
            output={
                "url": session.current_url,
                "title": session.current_title,
                "history": "not implemented",
            },
        )

    async def forward(
        self,
        session: BrowserSession,
    ) -> ProviderResult:
        """
        Navigate forward.

        Browser history will be implemented later.
        """

        if not self.is_running:
            return ProviderResult.failure(
                "Browser provider is not running.",
            )

        if not session.is_active:
            return ProviderResult.failure(
                "Browser session is closed.",
            )

        await self.adapter.forward(
            session,
        )

        return ProviderResult.ok(
            output={
                "url": session.current_url,
                "title": session.current_title,
                "history": "not implemented",
            },
        )

    async def refresh(
        self,
        session: BrowserSession,
    ) -> ProviderResult:
        """
        Refresh the current page.

        This placeholder implementation simply reports success.
        Future implementations will delegate to BrowserUse.
        """

        if not self.is_running:
            return ProviderResult.failure(
                "Browser provider is not running.",
            )

        if not session.is_active:
            return ProviderResult.failure(
                "Browser session is closed.",
            )

        await self.adapter.refresh(
            session,
        )

        return ProviderResult.ok(
            output={
                "url": session.current_url,
                "title": session.current_title,
                "refreshed": True,
            },
        )

    # ------------------------------------------------------------------
    # Interaction
    # ------------------------------------------------------------------

    async def click(
        self,
        session: BrowserSession,
        selector: str,
    ) -> ProviderResult:
        """
        Click an element.

        Placeholder implementation.
        """

        if not self.is_running:
            return ProviderResult.failure(
                "Browser provider is not running.",
            )

        if not session.is_active:
            return ProviderResult.failure(
                "Browser session is closed.",
            )

        await self.adapter.click(
            session,
            selector,
        )

        return ProviderResult.ok(
            output={
                "action": "click",
                "selector": selector,
                "url": session.current_url,
            },
        )

    async def type(
        self,
        session: BrowserSession,
        selector: str,
        text: str,
    ) -> ProviderResult:
        """
        Type text into an element.

        Placeholder implementation.
        """

        if not self.is_running:
            return ProviderResult.failure(
                "Browser provider is not running.",
            )

        if not session.is_active:
            return ProviderResult.failure(
                "Browser session is closed.",
            )

        await self.adapter.type(
            session,
            selector,
            text,
        )

        return ProviderResult.ok(
            output={
                "action": "type",
                "selector": selector,
                "text": text,
            },
        )

    async def press(
        self,
        session: BrowserSession,
        key: str,
    ) -> ProviderResult:
        """
        Press a keyboard key.

        Placeholder implementation.
        """

        if not self.is_running:
            return ProviderResult.failure(
                "Browser provider is not running.",
            )

        if not session.is_active:
            return ProviderResult.failure(
                "Browser session is closed.",
            )

        await self.adapter.press(
            session,
            key,
        )

        return ProviderResult.ok(
            output={
                "action": "press",
                "key": key,
            },
        )

    async def scroll(
        self,
        session: BrowserSession,
        *,
        x: int = 0,
        y: int = 0,
    ) -> ProviderResult:
        """
        Scroll the current page.

        Placeholder implementation.
        """

        if not self.is_running:
            return ProviderResult.failure(
                "Browser provider is not running.",
            )

        if not session.is_active:
            return ProviderResult.failure(
                "Browser session is closed.",
            )

        await self.adapter.scroll(
            session,
            x=x,
            y=y,
        )

        return ProviderResult.ok(
            output={
                "action": "scroll",
                "x": x,
                "y": y,
                "url": session.current_url,
            },
        )

    # ------------------------------------------------------------------
    # Information
    # ------------------------------------------------------------------

    async def screenshot(
        self,
        session: BrowserSession,
    ) -> ProviderResult:
        """
        Capture a screenshot.

        Placeholder implementation.
        """

        if not self.is_running:
            return ProviderResult.failure(
                "Browser provider is not running.",
            )

        if not session.is_active:
            return ProviderResult.failure(
                "Browser session is closed.",
            )

        image = await self.adapter.screenshot(
            session,
        )

        return ProviderResult.ok(
            output={
                "action": "screenshot",
                "url": session.current_url,
                "image": image,
            },
        )

    async def content(
        self,
        session: BrowserSession,
    ) -> ProviderResult:
        """
        Return the current page content.

        This initial implementation returns placeholder HTML.
        Future versions will retrieve the DOM through BrowserUse.
        """

        if not self.is_running:
            return ProviderResult.failure(
                "Browser provider is not running.",
            )

        if not session.is_active:
            return ProviderResult.failure(
                "Browser session is closed.",
            )

        html = await self.adapter.content(
            session,
        )

        return ProviderResult.ok(
            output=html,
        )

    async def current_url(
        self,
        session: BrowserSession,
    ) -> ProviderResult:
        """
        Return the current URL.
        """

        if not self.is_running:
            return ProviderResult.failure(
                "Browser provider is not running.",
            )

        if not session.is_active:
            return ProviderResult.failure(
                "Browser session is closed.",
            )

        url = await self.adapter.current_url(
            session,
        )

        return ProviderResult.ok(
            output=url,
        )

    async def title(
        self,
        session: BrowserSession,
    ) -> ProviderResult:
        """
        Return the current page title.
        """

        if not self.is_running:
            return ProviderResult.failure(
                "Browser provider is not running.",
            )

        if not session.is_active:
            return ProviderResult.failure(
                "Browser session is closed.",
            )

        title = await self.adapter.title(
            session,
        )

        return ProviderResult.ok(
            output=title,
        )

        # ------------------------------------------------------------------
    # Generic Execution
    # ------------------------------------------------------------------

    async def execute(
        self,
        capability: str,
        *,
        arguments: dict[str, object] | None = None,
    ) -> ProviderResult:
        """
        Execute a browser capability.
        """

        arguments = arguments or {}

        session = arguments.get(
            "session",
        )

        if not isinstance(
            session,
            BrowserSession,
        ):
            raise ValueError(
                "A BrowserSession is required."
            )

        match capability:

            case "browser.navigate":
                return await self.navigate(
                    session,
                    str(
                        arguments["url"],
                    ),
                )

            case "browser.back":
                return await self.back(
                    session,
                )

            case "browser.forward":
                return await self.forward(
                    session,
                )

            case "browser.refresh":
                return await self.refresh(
                    session,
                )

            case "browser.click":
                return await self.click(
                    session,
                    str(
                        arguments["selector"],
                    ),
                )

            case "browser.type":
                return await self.type(
                    session,
                    str(
                        arguments["selector"],
                    ),
                    str(
                        arguments["text"],
                    ),
                )

            case "browser.press":
                return await self.press(
                    session,
                    str(
                        arguments["key"],
                    ),
                )

            case "browser.scroll":
                return await self.scroll(
                    session,
                    x=int(
                        cast(
                            int | str,
                            arguments.get(
                                "x",
                                0,
                            ),
                        ),
                    ),
                    y=int(
                        cast(
                            int | str,
                            arguments.get(
                                "y",
                                0,
                            ),
                        ),
                    ),
                )

            case "browser.screenshot":
                return await self.screenshot(
                    session,
                )

            case "browser.content":
                return await self.content(
                    session,
                )

            case "browser.current_url":
                return await self.current_url(
                    session,
                )

            case "browser.title":
                return await self.title(
                    session,
                )

            case _:
                raise ValueError(
                    f"Unsupported capability "
                    f"'{capability}'."
                )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Provider diagnostics.
        """

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "running": self.is_running,
                "config": self.config.diagnostics(),
            },
        )

        return diagnostics