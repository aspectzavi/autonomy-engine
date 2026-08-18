"""
Playwright browser provider.

Concrete BrowserProvider implementation backed by Playwright.

This is the primary browser automation backend: every navigate/click/
type/scroll/screenshot call executes directly against a real Chromium
page through Playwright with no LLM involvement per action. An agent
(or anything else driving the browser) decides once what to do; this
provider carries that decision out deterministically. This keeps
per-step token cost at zero regardless of how many browser actions a
task needs.

A separate LLM-driven provider (browser_use_provider.py) can be
registered instead of this one, behind the same BrowserProvider
abstraction, for tasks that genuinely need autonomous "figure out how
to accomplish this on an unfamiliar page" behavior -- this provider is
not that, by design.

The underlying Playwright driver (browser, contexts, pages) is started
lazily on first use rather than at construction, so importing or
registering this provider never launches a browser process by itself.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, cast

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

if TYPE_CHECKING:
    from playwright.async_api import (
        Browser,
        Page,
        Playwright,
    )

_CAPABILITIES = frozenset(
    {
        "navigate",
        "back",
        "forward",
        "refresh",
        "click",
        "type",
        "press",
        "scroll",
        "screenshot",
        "content",
        "text_content",
        "wait_for",
        "upload",
        "download",
        "current_url",
        "title",
        "extract_links",
        "extract_structured",
    },
)

#
# Generic (site-agnostic) DOM extraction. These run in the page's own
# JS context via page.evaluate()/eval_on_selector_all(), so they work
# on any page's markup without needing to know its selectors ahead of
# time.
#

_EXTRACT_LINKS_JS = """
elements => elements.map(el => ({
    href: el.href,
    text: (el.innerText || el.textContent || "").trim(),
    rel: el.getAttribute("rel"),
}))
"""

_EXTRACT_STRUCTURED_JS = """
() => {
    const headings = Array.from(
        document.querySelectorAll("h1, h2, h3, h4, h5, h6"),
    ).map(el => ({
        level: parseInt(el.tagName.substring(1), 10),
        text: (el.innerText || el.textContent || "").trim(),
    })).filter(h => h.text.length > 0);

    const links = Array.from(
        document.querySelectorAll("a[href]"),
    ).map(el => ({
        href: el.href,
        text: (el.innerText || el.textContent || "").trim(),
        rel: el.getAttribute("rel"),
    }));

    const images = Array.from(
        document.querySelectorAll("img[src]"),
    ).map(el => ({
        src: el.src,
        alt: el.getAttribute("alt") || "",
    }));

    const tables = Array.from(
        document.querySelectorAll("table"),
    ).map(table => {
        const rows = Array.from(table.querySelectorAll("tr"));
        return rows.map(row =>
            Array.from(row.querySelectorAll("th, td")).map(
                cell => (cell.innerText || cell.textContent || "").trim(),
            ),
        );
    });

    const metaDescription = document.querySelector(
        'meta[name="description"]',
    );

    const body = document.body;

    return {
        url: window.location.href,
        title: document.title,
        meta_description: metaDescription
            ? metaDescription.getAttribute("content")
            : null,
        headings: headings,
        text: body
            ? (body.innerText || body.textContent || "").trim()
            : "",
        links: links,
        images: images,
        tables: tables,
    };
}
"""


class PlaywrightBrowserProvider(BrowserProvider):
    """
    Browser automation backed directly by Playwright.
    """

    def __init__(
        self,
        *,
        config: BrowserConfig | None = None,
    ) -> None:
        super().__init__(
            metadata=ProviderMetadata(
                name="playwright",
                version="1.0.0",
                description=(
                    "Deterministic Playwright-backed browser "
                    "automation."
                ),
                tags=frozenset({"browser", "playwright"}),
            ),
        )

        self._config = (
            config
            if config is not None
            else BrowserConfig()
        )

        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._pages: dict[str, Page] = {}

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def config(
        self,
    ) -> BrowserConfig:
        """
        Active browser configuration.
        """

        return self._config

    @property
    def is_running(
        self,
    ) -> bool:
        """
        Whether the underlying browser process is running.
        """

        return (
            self._browser is not None
            and self._browser.is_connected()
        )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(
        self,
    ) -> None:
        """
        Launch the underlying Playwright browser, if not running.

        Idempotent: calling this while already running is a no-op.
        """

        if self.is_running:
            return

        from playwright.async_api import (
            async_playwright,
        )

        if self._playwright is None:
            self._playwright = (
                await async_playwright().start()
            )

        self._browser = (
            await self._playwright.chromium.launch(
                headless=self._config.headless,
                slow_mo=self._config.slow_mo,
                executable_path=(
                    self._config.executable_path
                ),
                args=list(self._config.args),
            )
        )

    async def stop(
        self,
    ) -> None:
        """
        Close every open page and shut down the browser.
        """

        self._pages.clear()

        if self._browser is not None:
            await self._browser.close()
            self._browser = None

        if self._playwright is not None:
            await self._playwright.stop()
            self._playwright = None

    # ------------------------------------------------------------------
    # Session Management
    # ------------------------------------------------------------------

    async def create_session(
        self,
    ) -> BrowserSession:
        """
        Open a new browser page as a session.
        """

        await self.start()

        assert self._browser is not None

        context = await self._browser.new_context(
            viewport={
                "width": self._config.viewport_width,
                "height": self._config.viewport_height,
            },
            user_agent=self._config.user_agent,
            locale=self._config.locale,
            timezone_id=self._config.timezone,
            accept_downloads=(
                self._config.accept_downloads
            ),
            ignore_https_errors=(
                self._config.ignore_https_errors
            ),
        )

        context.set_default_timeout(
            self._config.timeout * 1000,
        )

        context.set_default_navigation_timeout(
            self._config.navigation_timeout * 1000,
        )

        page = await context.new_page()

        session = BrowserSession(
            backend=page,
        )

        self._pages[session.id] = page

        return session

    async def close_session(
        self,
        session: BrowserSession,
    ) -> None:
        """
        Close a session's page and its browser context.
        """

        page = self._pages.pop(
            session.id,
            None,
        )

        if page is not None:
            await page.context.close()

        session.close()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _page(
        self,
        session: BrowserSession,
    ) -> Page:
        page = self._pages.get(session.id)

        if page is None:
            raise ValueError(
                f"No active page for session '{session.id}'. "
                "Was the session created via this provider?",
            )

        return page

    async def _run(
        self,
        session: BrowserSession,
        action: Callable[["Page"], Awaitable[object]],
    ) -> ProviderResult:
        """
        Run a Playwright action against a session's page, converting
        exceptions into a ProviderResult instead of propagating them.
        """

        from datetime import UTC, datetime

        started_at = datetime.now(UTC)

        try:
            page = self._page(session)
            output = await action(page)
        except Exception as exc:  # noqa: BLE001
            return ProviderResult.failure(
                str(exc),
                started_at=started_at,
            )

        session.update(
            url=page.url,
            title=await page.title(),
        )

        return ProviderResult.ok(
            output=output,
            started_at=started_at,
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

        return await self._run(
            session,
            lambda page: page.goto(url),
        )

    async def back(
        self,
        session: BrowserSession,
    ) -> ProviderResult:
        """
        Navigate backward.
        """

        return await self._run(
            session,
            lambda page: page.go_back(),
        )

    async def forward(
        self,
        session: BrowserSession,
    ) -> ProviderResult:
        """
        Navigate forward.
        """

        return await self._run(
            session,
            lambda page: page.go_forward(),
        )

    async def refresh(
        self,
        session: BrowserSession,
    ) -> ProviderResult:
        """
        Refresh the current page.
        """

        return await self._run(
            session,
            lambda page: page.reload(),
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
        """

        return await self._run(
            session,
            lambda page: page.click(selector),
        )

    async def type(
        self,
        session: BrowserSession,
        selector: str,
        text: str,
    ) -> ProviderResult:
        """
        Type into an element.
        """

        return await self._run(
            session,
            lambda page: page.fill(selector, text),
        )

    async def press(
        self,
        session: BrowserSession,
        key: str,
    ) -> ProviderResult:
        """
        Press a keyboard key.
        """

        return await self._run(
            session,
            lambda page: page.keyboard.press(key),
        )

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

        return await self._run(
            session,
            lambda page: page.mouse.wheel(x, y),
        )

    # ------------------------------------------------------------------
    # Information
    # ------------------------------------------------------------------

    async def screenshot(
        self,
        session: BrowserSession,
    ) -> ProviderResult:
        """
        Capture a screenshot, returned as raw PNG bytes.
        """

        return await self._run(
            session,
            lambda page: page.screenshot(),
        )

    async def content(
        self,
        session: BrowserSession,
    ) -> ProviderResult:
        """
        Retrieve the current page HTML.
        """

        return await self._run(
            session,
            lambda page: page.content(),
        )

    async def text_content(
        self,
        session: BrowserSession,
    ) -> ProviderResult:
        """
        Retrieve the current page's visible text.
        """

        return await self._run(
            session,
            lambda page: page.inner_text("body"),
        )

    async def wait_for(
        self,
        session: BrowserSession,
        *,
        selector: str | None = None,
        timeout: float | None = None,
    ) -> ProviderResult:
        """
        Wait for a selector to appear, or a fixed duration.
        """

        timeout_ms = (
            timeout * 1000
            if timeout is not None
            else None
        )

        async def _wait(page: Page) -> None:
            if selector is not None:
                await page.wait_for_selector(
                    selector,
                    timeout=timeout_ms,
                )
                return

            await page.wait_for_timeout(
                timeout_ms
                if timeout_ms is not None
                else self._config.timeout * 1000,
            )

        return await self._run(session, _wait)

    async def upload(
        self,
        session: BrowserSession,
        selector: str,
        file_path: str,
    ) -> ProviderResult:
        """
        Attach a local file to a file-input element.
        """

        return await self._run(
            session,
            lambda page: page.set_input_files(
                selector,
                file_path,
            ),
        )

    async def download(
        self,
        session: BrowserSession,
        *,
        trigger_selector: str,
        destination: str,
    ) -> ProviderResult:
        """
        Click an element that triggers a download and save it.
        """

        async def _download(page: Page) -> str:
            async with page.expect_download() as download_info:
                await page.click(trigger_selector)

            download = await download_info.value
            await download.save_as(destination)

            return destination

        return await self._run(session, _download)

    async def current_url(
        self,
        session: BrowserSession,
    ) -> ProviderResult:
        """
        Retrieve the current page URL.
        """

        async def _get(page: Page) -> str:
            return page.url

        return await self._run(session, _get)

    async def title(
        self,
        session: BrowserSession,
    ) -> ProviderResult:
        """
        Retrieve the current page title.
        """

        return await self._run(
            session,
            lambda page: page.title(),
        )

    # ------------------------------------------------------------------
    # Generic extraction
    # ------------------------------------------------------------------

    async def extract_links(
        self,
        session: BrowserSession,
    ) -> ProviderResult:
        """
        Extract every link on the current page.
        """

        return await self._run(
            session,
            lambda page: page.eval_on_selector_all(
                "a[href]",
                _EXTRACT_LINKS_JS,
            ),
        )

    async def extract_structured(
        self,
        session: BrowserSession,
    ) -> ProviderResult:
        """
        Extract a generic structured summary of the current page.
        """

        return await self._run(
            session,
            lambda page: page.evaluate(
                _EXTRACT_STRUCTURED_JS,
            ),
        )

    # ------------------------------------------------------------------
    # Provider Interface
    # ------------------------------------------------------------------

    def supports(
        self,
        capability: str,
    ) -> bool:
        """
        Determine whether this provider supports a capability.
        """

        return capability in _CAPABILITIES

    async def execute(
        self,
        capability: str,
        *,
        arguments: dict[str, object] | None = None,
    ) -> ProviderResult:
        """
        Execute a browser capability by name.

        This is the generic entry point (matching the Provider
        contract); the typed methods above (navigate(), click(), ...)
        are the preferred way to call this provider directly.
        """

        if not self.supports(capability):
            return ProviderResult.failure(
                f"Unsupported browser capability: '{capability}'.",
            )

        args = arguments or {}

        session = cast(
            "BrowserSession | None",
            args.get("session"),
        )

        if session is None:
            return ProviderResult.failure(
                "Missing required argument 'session'.",
            )

        if capability == "navigate":
            return await self.navigate(
                session,
                str(args.get("url", "")),
            )

        if capability == "back":
            return await self.back(session)

        if capability == "forward":
            return await self.forward(session)

        if capability == "refresh":
            return await self.refresh(session)

        if capability == "click":
            return await self.click(
                session,
                str(args.get("selector", "")),
            )

        if capability == "type":
            return await self.type(
                session,
                str(args.get("selector", "")),
                str(args.get("text", "")),
            )

        if capability == "press":
            return await self.press(
                session,
                str(args.get("key", "")),
            )

        if capability == "scroll":
            return await self.scroll(
                session,
                x=int(cast("str | int", args.get("x", 0))),
                y=int(cast("str | int", args.get("y", 0))),
            )

        if capability == "screenshot":
            return await self.screenshot(session)

        if capability == "content":
            return await self.content(session)

        if capability == "text_content":
            return await self.text_content(session)

        if capability == "wait_for":
            raw_timeout = args.get("timeout")

            return await self.wait_for(
                session,
                selector=cast(
                    "str | None",
                    args.get("selector"),
                ),
                timeout=(
                    float(cast("str | float", raw_timeout))
                    if raw_timeout is not None
                    else None
                ),
            )

        if capability == "upload":
            return await self.upload(
                session,
                str(args.get("selector", "")),
                str(args.get("file_path", "")),
            )

        if capability == "download":
            return await self.download(
                session,
                trigger_selector=str(
                    args.get("trigger_selector", ""),
                ),
                destination=str(
                    args.get("destination", ""),
                ),
            )

        if capability == "current_url":
            return await self.current_url(session)

        if capability == "title":
            return await self.title(session)

        if capability == "extract_links":
            return await self.extract_links(session)

        return await self.extract_structured(session)

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return provider diagnostics.
        """

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "is_running": self.is_running,
                "open_sessions": len(self._pages),
                "config": self._config.diagnostics(),
            },
        )

        return diagnostics
