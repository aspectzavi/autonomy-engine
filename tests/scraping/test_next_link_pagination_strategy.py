"""
Next-link pagination strategy tests.
"""

from __future__ import annotations

import pytest

from backend.core.scraping.next_link_pagination_strategy import (
    NextLinkPaginationStrategy,
)
from tests.scraping.fakes import ScriptedBrowserProvider


@pytest.mark.asyncio
async def test_prefers_rel_next_over_text_matching() -> None:
    provider = ScriptedBrowserProvider(
        pages={
            "https://site.com/1": {
                "links": [
                    {"href": "https://site.com/wrong", "text": "Next", "rel": None},
                    {"href": "https://site.com/2", "text": "later", "rel": "next"},
                ],
            },
        },
    )
    session = await provider.create_session()
    await provider.navigate(session, "https://site.com/1")

    strategy = NextLinkPaginationStrategy()

    next_url = await strategy.next_url(
        provider=provider,
        session=session,
        current_url="https://site.com/1",
        page_number=1,
    )

    assert next_url == "https://site.com/2"


@pytest.mark.asyncio
async def test_falls_back_to_text_matching() -> None:
    provider = ScriptedBrowserProvider(
        pages={
            "https://site.com/1": {
                "links": [
                    {"href": "https://site.com/about", "text": "About", "rel": None},
                    {"href": "https://site.com/2", "text": "Next", "rel": None},
                ],
            },
        },
    )
    session = await provider.create_session()
    await provider.navigate(session, "https://site.com/1")

    strategy = NextLinkPaginationStrategy()

    next_url = await strategy.next_url(
        provider=provider,
        session=session,
        current_url="https://site.com/1",
        page_number=1,
    )

    assert next_url == "https://site.com/2"


@pytest.mark.asyncio
async def test_returns_none_when_no_next_link_found() -> None:
    provider = ScriptedBrowserProvider(
        pages={
            "https://site.com/1": {
                "links": [
                    {"href": "https://site.com/about", "text": "About", "rel": None},
                ],
            },
        },
    )
    session = await provider.create_session()
    await provider.navigate(session, "https://site.com/1")

    strategy = NextLinkPaginationStrategy()

    next_url = await strategy.next_url(
        provider=provider,
        session=session,
        current_url="https://site.com/1",
        page_number=1,
    )

    assert next_url is None


@pytest.mark.asyncio
async def test_custom_text_patterns() -> None:
    provider = ScriptedBrowserProvider(
        pages={
            "https://site.com/1": {
                "links": [
                    {"href": "https://site.com/2", "text": "More Posts", "rel": None},
                ],
            },
        },
    )
    session = await provider.create_session()
    await provider.navigate(session, "https://site.com/1")

    strategy = NextLinkPaginationStrategy(
        text_patterns=("more posts",),
    )

    next_url = await strategy.next_url(
        provider=provider,
        session=session,
        current_url="https://site.com/1",
        page_number=1,
    )

    assert next_url == "https://site.com/2"
