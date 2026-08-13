"""
Application dependency providers.

Provides kernel application instances
to API routes.
"""

from __future__ import annotations

from backend.core.kernel.application import Application


_application: Application | None = None


def set_application(
    application: Application,
) -> None:
    """
    Set global application instance.
    """

    global _application

    _application = application


def get_application() -> Application:
    """
    Retrieve application instance.
    """

    if _application is None:
        raise RuntimeError(
            "Application has not been initialized."
        )

    return _application