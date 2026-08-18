"""
Fake browser provider.

Records every call made to it and returns canned ProviderResults, so
browser tool tests can verify argument validation and delegation
without launching a real browser.
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


class FakeBrowserProvider(BrowserProvider):
    """
    Test double recording every call made to it.
    """

    def __init__(self) -> None:
        super().__init__(
            metadata=ProviderMetadata(
                name="fake",
                version="0.0.0",
            ),
        )
        self.calls: list[tuple[str, tuple, dict]] = []
        self.next_result = ProviderResult.ok(output="ok")
        self._running = False
        self._sessions: dict[str, BrowserSession] = {}

    def _record(self, name: str, *args: object, **kwargs: object) -> ProviderResult:
        self.calls.append((name, args, kwargs))
        return self.next_result

    async def start(self) -> None:
        self._running = True

    async def stop(self) -> None:
        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running

    async def create_session(self) -> BrowserSession:
        session = BrowserSession()
        self._sessions[session.id] = session
        return session

    async def close_session(self, session: BrowserSession) -> None:
        self._sessions.pop(session.id, None)
        session.close()

    async def navigate(self, session, url):
        return self._record("navigate", session, url)

    async def back(self, session):
        return self._record("back", session)

    async def forward(self, session):
        return self._record("forward", session)

    async def refresh(self, session):
        return self._record("refresh", session)

    async def click(self, session, selector):
        return self._record("click", session, selector)

    async def type(self, session, selector, text):
        return self._record("type", session, selector, text)

    async def press(self, session, key):
        return self._record("press", session, key)

    async def scroll(self, session, *, x=0, y=0):
        return self._record("scroll", session, x=x, y=y)

    async def screenshot(self, session):
        return self._record("screenshot", session)

    async def content(self, session):
        return self._record("content", session)

    async def text_content(self, session):
        return self._record("text_content", session)

    async def wait_for(self, session, *, selector=None, timeout=None):
        return self._record(
            "wait_for", session, selector=selector, timeout=timeout,
        )

    async def upload(self, session, selector, file_path):
        return self._record("upload", session, selector, file_path)

    async def download(self, session, *, trigger_selector, destination):
        return self._record(
            "download",
            session,
            trigger_selector=trigger_selector,
            destination=destination,
        )

    async def current_url(self, session):
        return self._record("current_url", session)

    async def title(self, session):
        return self._record("title", session)

    async def extract_links(self, session):
        return self._record("extract_links", session)

    async def extract_structured(self, session):
        return self._record("extract_structured", session)

    def supports(self, capability: str) -> bool:
        return True

    async def execute(self, capability, *, arguments=None):
        return self._record("execute", capability, arguments=arguments)
