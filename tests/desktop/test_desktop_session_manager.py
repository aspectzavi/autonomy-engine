"""
Desktop session manager tests.
"""

from __future__ import annotations

import pytest

from backend.core.providers.desktop.desktop_session_manager import (
    DesktopSessionManager,
)
from tests.desktop.fakes import FakeDesktopProvider


@pytest.mark.asyncio
async def test_get_default_session_creates_lazily() -> None:
    provider = FakeDesktopProvider()
    manager = DesktopSessionManager(provider=provider)

    session = await manager.get_default_session()

    assert session.is_active


@pytest.mark.asyncio
async def test_get_default_session_reuses_the_same_session() -> None:
    provider = FakeDesktopProvider()
    manager = DesktopSessionManager(provider=provider)

    first = await manager.get_default_session()
    second = await manager.get_default_session()

    assert first is second


@pytest.mark.asyncio
async def test_get_default_session_recreates_after_close() -> None:
    provider = FakeDesktopProvider()
    manager = DesktopSessionManager(provider=provider)

    first = await manager.get_default_session()
    first.close()

    second = await manager.get_default_session()

    assert second is not first


@pytest.mark.asyncio
async def test_close_clears_the_default_session() -> None:
    provider = FakeDesktopProvider()
    manager = DesktopSessionManager(provider=provider)

    await manager.get_default_session()
    await manager.close()

    diagnostics = manager.diagnostics()
    assert diagnostics["has_default_session"] is False


@pytest.mark.asyncio
async def test_close_without_a_session_is_a_no_op() -> None:
    provider = FakeDesktopProvider()
    manager = DesktopSessionManager(provider=provider)

    await manager.close()
