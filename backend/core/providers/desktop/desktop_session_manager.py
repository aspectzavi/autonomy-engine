"""
Desktop session manager.

Owns a single default DesktopSession, created lazily on first use and
reused across subsequent desktop tool calls, the same way
BrowserSessionManager does for browser sessions.
"""

from __future__ import annotations

from backend.core.providers.desktop.desktop_provider import (
    DesktopProvider,
)
from backend.core.providers.desktop.desktop_session import (
    DesktopSession,
)


class DesktopSessionManager:
    """
    Manages the default desktop session for a DesktopProvider.
    """

    def __init__(
        self,
        *,
        provider: DesktopProvider,
    ) -> None:
        self._provider = provider
        self._default_session: DesktopSession | None = None

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def provider(
        self,
    ) -> DesktopProvider:
        """
        The desktop provider sessions are opened through.
        """

        return self._provider

    # ------------------------------------------------------------------
    # Sessions
    # ------------------------------------------------------------------

    async def get_default_session(
        self,
    ) -> DesktopSession:
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
