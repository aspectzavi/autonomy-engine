"""
Fake desktop provider.

Records every call made to it and returns canned ProviderResults, so
desktop tool tests can verify argument validation and delegation
without a real window.
"""

from __future__ import annotations

from backend.core.providers.desktop.desktop_provider import (
    DesktopProvider,
)
from backend.core.providers.desktop.desktop_session import (
    DesktopSession,
)
from backend.core.providers.provider_metadata import (
    ProviderMetadata,
)
from backend.core.providers.provider_result import (
    ProviderResult,
)


class FakeDesktopProvider(DesktopProvider):
    """
    Test double recording every call made to it.
    """

    def __init__(self) -> None:
        super().__init__(
            metadata=ProviderMetadata(name="fake", version="0.0.0"),
        )
        self.calls: list[tuple[str, tuple, dict]] = []
        self.next_result = ProviderResult.ok(output="ok")
        self._running = False

    def _record(self, call_name: str, *args: object, **kwargs: object) -> ProviderResult:
        self.calls.append((call_name, args, kwargs))
        return self.next_result

    async def start(self) -> None:
        self._running = True

    async def stop(self) -> None:
        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running

    async def create_session(self) -> DesktopSession:
        return DesktopSession()

    async def close_session(self, session: DesktopSession) -> None:
        session.close()

    async def list_windows(self, session):
        return self._record("list_windows", session)

    async def connect_window(self, session, *, title=None, title_pattern=None, process_id=None):
        return self._record(
            "connect_window", session,
            title=title, title_pattern=title_pattern, process_id=process_id,
        )

    async def launch(self, session, path, *, arguments=()):
        return self._record("launch", session, path, arguments=arguments)

    async def click_element(self, session, *, name=None, automation_id=None, control_type=None):
        return self._record(
            "click_element", session,
            name=name, automation_id=automation_id, control_type=control_type,
        )

    async def type_into_element(self, session, text, *, name=None, automation_id=None, control_type=None):
        return self._record(
            "type_into_element", session, text,
            name=name, automation_id=automation_id, control_type=control_type,
        )

    async def get_element_text(self, session, *, name=None, automation_id=None, control_type=None):
        return self._record(
            "get_element_text", session,
            name=name, automation_id=automation_id, control_type=control_type,
        )

    async def extract_structured(self, session):
        return self._record("extract_structured", session)

    async def click_at(self, session, x, y, *, button="left", clicks=1):
        return self._record("click_at", session, x, y, button=button, clicks=clicks)

    async def move_to(self, session, x, y):
        return self._record("move_to", session, x, y)

    async def drag(self, session, *, from_x, from_y, to_x, to_y):
        return self._record(
            "drag", session,
            from_x=from_x, from_y=from_y, to_x=to_x, to_y=to_y,
        )

    async def scroll_at(self, session, x, y, amount):
        return self._record("scroll_at", session, x, y, amount)

    async def type_text(self, session, text):
        return self._record("type_text", session, text)

    async def press_key(self, session, key):
        return self._record("press_key", session, key)

    async def screenshot(self, session):
        return self._record("screenshot", session)

    async def current_window_title(self, session):
        return self._record("current_window_title", session)

    def supports(self, capability: str) -> bool:
        return True

    async def execute(self, capability, *, arguments=None):
        return self._record("execute", capability, arguments=arguments)
