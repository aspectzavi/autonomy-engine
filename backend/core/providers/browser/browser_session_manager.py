"""
Browser session manager.

Owns a single default BrowserSession, created lazily on first use and
reused across subsequent browser tool calls. This is what makes a
sequence of browser tool calls (navigate, then click, then extract
text, ...) act on the same page rather than each opening a fresh tab.

Deliberately minimal: one default session is enough for the common
case of a single agent driving a single browser at a time. Multi-
session support can be added on top of BrowserProvider.create_session()
later without changing this class's contract.
"""

from __future__ import annotations

from backend.core.providers.browser.browser_provider import (
    BrowserProvider,
)
from backend.core.providers.browser.browser_session import (
    BrowserSession,
)


class BrowserSessionManager:
    """
    Manages the default browser session for a BrowserProvider.
    """

    def __init__(
        self,
        *,
        provider: BrowserProvider,
    ) -> None:
        self._provider = provider
        self._default_session: BrowserSession | None = None

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def provider(
        self,
    ) -> BrowserProvider:
        """
        The browser provider sessions are opened through.
        """

        return self._provider

    # ------------------------------------------------------------------
    # Sessions
    # ------------------------------------------------------------------

    async def get_default_session(
        self,
    ) -> BrowserSession:
        """
        Return the default session, opening one if none exists yet.
        """

        if (
            self._default_session is None
            or not self._default_session.is_active
        ):
            self._default_session = (
                await self._provider.create_session()
            )

        return self._default_session

    async def close(
        self,
    ) -> None:
        """
        Close the default session, if one is open.
        """

        if self._default_session is not None:
            await self._provider.close_session(
                self._default_session,
            )
            self._default_session = None

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return session manager diagnostics.
        """

        return {
            "has_default_session": (
                self._default_session is not None
            ),
            "session": (
                self._default_session.diagnostics()
                if self._default_session is not None
                else None
            ),
        }
