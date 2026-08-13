"""
Application entrypoint.

Starts the autonomous engine runtime.

The main module is responsible only for:

- creating the application
- running lifecycle
- handling shutdown

All construction belongs to KernelBootstrap.
"""

from __future__ import annotations

import asyncio
import signal
from types import FrameType

from backend.core.kernel.application import Application


application = Application()


_shutdown_event = asyncio.Event()


def _handle_shutdown(
    signal_number: int,
    frame: FrameType | None,
) -> None:
    """
    Handle operating system shutdown signals.
    """
    _shutdown_event.set()


async def run() -> None:
    """
    Run application lifecycle.
    """

    await application.start()

    await _shutdown_event.wait()

    await application.stop()


def configure_signals() -> None:
    """
    Configure graceful shutdown signals.
    """

    signal.signal(
        signal.SIGINT,
        _handle_shutdown,
    )

    signal.signal(
        signal.SIGTERM,
        _handle_shutdown,
    )


def main() -> None:
    """
    Application entrypoint.
    """

    configure_signals()

    asyncio.run(
        run()
    )


if __name__ == "__main__":
    main()