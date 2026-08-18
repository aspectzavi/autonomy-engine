"""
Scripted browser provider.

A fake BrowserProvider whose navigate()/extract_structured()/
extract_links() behavior is scripted per-URL, so WebScraper's crawl
loop (multi-page traversal, cycle detection, error handling) can be
tested deterministically without a real browser.
"""

from __future__ import annotations

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


class ScriptedBrowserProvider(BrowserProvider):
    """
    Fake provider with per-URL scripted navigate/extract behavior.
    """

    def __init__(
        self,
        pages: dict[str, dict],
    ) -> None:
        super().__init__(
            metadata=ProviderMetadata(name="scripted", version="0.0.0"),
        )
        self.pages = pages
        self.visited_urls: list[str] = []
        self._current_url: str | None = None

    async def start(self) -> None:
        pass

    async def stop(self) -> None:
        pass

    @property
    def is_running(self) -> bool:
        return True

    async def create_session(self) -> BrowserSession:
        return BrowserSession()

    async def close_session(self, session: BrowserSession) -> None:
        session.close()

    async def navigate(self, session, url):
        self.visited_urls.append(url)

        page = self.pages.get(url)

        if page is None or page.get("fail"):
            return ProviderResult.failure(
                f"Failed to load {url}",
            )

        self._current_url = url
        return ProviderResult.ok(output=None)

    async def back(self, session):
        return ProviderResult.ok(output=None)

    async def forward(self, session):
        return ProviderResult.ok(output=None)

    async def refresh(self, session):
        return ProviderResult.ok(output=None)

    async def click(self, session, selector):
        return ProviderResult.ok(output=None)

    async def type(self, session, selector, text):
        return ProviderResult.ok(output=None)

    async def press(self, session, key):
        return ProviderResult.ok(output=None)

    async def scroll(self, session, *, x=0, y=0):
        return ProviderResult.ok(output=None)

    async def screenshot(self, session):
        return ProviderResult.ok(output=b"")

    async def content(self, session):
        return ProviderResult.ok(output="")

    async def text_content(self, session):
        return ProviderResult.ok(output="")

    async def wait_for(self, session, *, selector=None, timeout=None):
        return ProviderResult.ok(output=None)

    async def upload(self, session, selector, file_path):
        return ProviderResult.ok(output=None)

    async def download(self, session, *, trigger_selector, destination):
        return ProviderResult.ok(output=None)

    async def current_url(self, session):
        return ProviderResult.ok(output=self._current_url)

    async def title(self, session):
        return ProviderResult.ok(output="")

    async def extract_links(self, session):
        page = self.pages.get(self._current_url, {})
        return ProviderResult.ok(output=page.get("links", []))

    async def extract_structured(self, session):
        page = self.pages.get(self._current_url)

        if page is None:
            return ProviderResult.failure("No page loaded.")

        if page.get("fail_extract"):
            return ProviderResult.failure("Extraction failed.")

        return ProviderResult.ok(
            output=page.get(
                "structured",
                {"title": self._current_url},
            ),
        )

    def supports(self, capability: str) -> bool:
        return True

    async def execute(self, capability, *, arguments=None):
        return ProviderResult.ok(output=None)
