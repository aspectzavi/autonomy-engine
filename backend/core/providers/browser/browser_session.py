"""
Browser session.

Represents a single browser automation session.

A session abstracts an individual browser context regardless of the
underlying implementation.

Examples:

- BrowserUse Agent
- Playwright BrowserContext
- Chrome DevTools session
- Selenium WebDriver

The remainder of the engine interacts only with BrowserSession.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4


@dataclass(slots=True)
class BrowserSession:
    """
    Browser automation session.
    """

    id: str = field(
        default_factory=lambda: str(uuid4()),
    )

    current_url: str = ""

    current_title: str = ""

    is_active: bool = True

    backend: object | None = None

    metadata: dict[str, object] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(
        self,
    ) -> None:
        """
        Mark the session as closed.
        """

        self.is_active = False

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------

    def update(
        self,
        *,
        url: str | None = None,
        title: str | None = None,
    ) -> None:
        """
        Update browser state.
        """

        if url is not None:
            self.current_url = url

        if title is not None:
            self.current_title = title

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Session diagnostics.
        """

        return {
            "id": self.id,
            "active": self.is_active,
            "url": self.current_url,
            "title": self.current_title,
            "backend": (
                type(self.backend).__name__
                if self.backend is not None
                else None
            ),
            "metadata": self.metadata,
        }