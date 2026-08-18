"""
Playwright browser provider integration tests.

Unlike the rest of tests/browser/ (which use a fake provider for
speed), these launch a real Chromium browser and hit a real page.
Slower, but they are what actually proves this backend works rather
than just type-checking against the BrowserProvider interface.
"""

from __future__ import annotations

import pytest

from backend.core.providers.browser.playwright_browser_provider import (
    PlaywrightBrowserProvider,
)

pytestmark = pytest.mark.asyncio


async def test_navigate_and_extract_text_against_a_real_page() -> None:
    provider = PlaywrightBrowserProvider()

    try:
        session = await provider.create_session()

        nav_result = await provider.navigate(
            session, "https://example.com",
        )
        assert nav_result.success

        text_result = await provider.text_content(session)
        assert text_result.success
        assert "Example Domain" in text_result.output

        title_result = await provider.title(session)
        assert title_result.success
        assert title_result.output == "Example Domain"
    finally:
        await provider.stop()


async def test_screenshot_returns_valid_png_bytes() -> None:
    provider = PlaywrightBrowserProvider()

    try:
        session = await provider.create_session()
        await provider.navigate(session, "https://example.com")

        result = await provider.screenshot(session)

        assert result.success
        #
        # PNG file signature.
        #
        assert result.output[:8] == b"\x89PNG\r\n\x1a\n"
    finally:
        await provider.stop()


async def test_session_tracks_current_url_and_title() -> None:
    provider = PlaywrightBrowserProvider()

    try:
        session = await provider.create_session()
        await provider.navigate(session, "https://example.com")

        assert session.current_url == "https://example.com/"
        assert session.current_title == "Example Domain"
    finally:
        await provider.stop()


async def test_navigating_to_an_invalid_url_fails_cleanly() -> None:
    provider = PlaywrightBrowserProvider()

    try:
        session = await provider.create_session()

        result = await provider.navigate(
            session, "https://this-domain-should-not-exist-xyz123.invalid",
        )

        assert not result.success
        assert result.error
    finally:
        await provider.stop()


async def test_start_is_idempotent() -> None:
    provider = PlaywrightBrowserProvider()

    try:
        await provider.start()
        assert provider.is_running

        await provider.start()
        assert provider.is_running
    finally:
        await provider.stop()


async def test_stop_without_start_is_a_no_op() -> None:
    provider = PlaywrightBrowserProvider()

    await provider.stop()

    assert not provider.is_running


async def test_acting_on_a_closed_session_fails_cleanly() -> None:
    provider = PlaywrightBrowserProvider()

    try:
        session = await provider.create_session()
        await provider.close_session(session)

        result = await provider.navigate(session, "https://example.com")

        assert not result.success
    finally:
        await provider.stop()


async def test_extract_links_against_a_real_page() -> None:
    provider = PlaywrightBrowserProvider()

    try:
        session = await provider.create_session()
        await provider.navigate(session, "https://example.com")

        result = await provider.extract_links(session)

        assert result.success
        links = result.output
        assert len(links) >= 1
        assert any(
            "iana.org" in (link.get("href") or "")
            for link in links
        )
        assert all(
            {"href", "text", "rel"} <= link.keys()
            for link in links
        )
    finally:
        await provider.stop()


async def test_extract_structured_against_a_real_page() -> None:
    provider = PlaywrightBrowserProvider()

    try:
        session = await provider.create_session()
        await provider.navigate(session, "https://example.com")

        result = await provider.extract_structured(session)

        assert result.success
        data = result.output
        assert data["title"] == "Example Domain"
        assert "Example Domain" in data["text"]
        assert isinstance(data["links"], list)
        assert isinstance(data["headings"], list)
        assert isinstance(data["images"], list)
        assert isinstance(data["tables"], list)
        assert data["headings"][0]["text"] == "Example Domain"
    finally:
        await provider.stop()
