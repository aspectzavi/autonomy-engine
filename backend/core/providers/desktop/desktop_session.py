"""
Desktop session.

Represents a single desktop automation session -- a window (or, once
connected, a specific application window) the provider is currently
driving.

The remainder of the engine interacts only with DesktopSession.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4


@dataclass(slots=True)
class DesktopSession:
    """
    Desktop automation session.
    """

    id: str = field(
        default_factory=lambda: str(uuid4()),
    )

    current_window_title: str = ""

    process_id: int | None = None

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
        window_title: str | None = None,
        process_id: int | None = None,
    ) -> None:
        """
        Update desktop session state.
        """

        if window_title is not None:
            self.current_window_title = window_title

        if process_id is not None:
            self.process_id = process_id

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
            "window_title": self.current_window_title,
            "process_id": self.process_id,
            "backend": (
                type(self.backend).__name__
                if self.backend is not None
                else None
            ),
            "metadata": self.metadata,
        }
