"""
Scrape tool tests.
"""

from __future__ import annotations

import pytest

from backend.core.providers.browser.browser_session_manager import (
    BrowserSessionManager,
)
from backend.core.tools.context import ToolContext
from backend.tools.browser.scrape_tool import ScrapeTool
from tests.scraping.fakes import ScriptedBrowserProvider


def _pages(count: int) -> dict:
    pages = {}
    for i in range(1, count + 1):
        url = f"https://site.com/{i}"
        next_url = f"https://site.com/{i + 1}" if i < count else None
        links = (
            [{"href": next_url, "text": "Next", "rel": "next"}]
            if next_url
            else []
        )
        pages[url] = {
            "structured": {
                "title": f"Page {i}",
                "links": links,
            },
            "links": links,
        }
    return pages


def _query_paginated_pages(count: int) -> dict:
    """
    Pages addressed by a ``?page=N`` query string, matching the
    "auto" pagination mode's default URL template
    ("https://site.com/listing?page={page}").
    """
    pages = {}
    for i in range(1, count + 1):
        url = (
            "https://site.com/listing"
            if i == 1
            else f"https://site.com/listing?page={i}"
        )
        pages[url] = {
            "structured": {
                "title": f"Page {i}",
                "links": [],
                "text": f"Listing page {i} with several products shown here.",
            },
            "links": [],
        }
    return pages


@pytest.mark.asyncio
async def test_requires_url() -> None:
    sessions = BrowserSessionManager(
        provider=ScriptedBrowserProvider(pages={}),
    )
    tool = ScrapeTool(sessions=sessions)

    result = await tool.execute(ToolContext(arguments={}))

    assert not result.success


@pytest.mark.asyncio
async def test_single_page_scrape() -> None:
    sessions = BrowserSessionManager(
        provider=ScriptedBrowserProvider(pages=_pages(1)),
    )
    tool = ScrapeTool(sessions=sessions)

    result = await tool.execute(
        ToolContext(arguments={"url": "https://site.com/1"}),
    )

    assert result.success
    assert result.output["page_count"] == 1
    assert result.output["pages"][0]["title"] == "Page 1"


@pytest.mark.asyncio
async def test_multi_page_scrape_defaults_to_auto_page_pagination() -> None:
    sessions = BrowserSessionManager(
        provider=ScriptedBrowserProvider(
            pages=_query_paginated_pages(3),
        ),
    )
    tool = ScrapeTool(sessions=sessions)

    result = await tool.execute(
        ToolContext(
            arguments={
                "url": "https://site.com/listing",
                "max_pages": 3,
            },
        ),
    )

    assert result.success
    assert result.output["page_count"] == 3


@pytest.mark.asyncio
async def test_multi_page_scrape_with_explicit_next_link() -> None:
    sessions = BrowserSessionManager(
        provider=ScriptedBrowserProvider(pages=_pages(3)),
    )
    tool = ScrapeTool(sessions=sessions)

    result = await tool.execute(
        ToolContext(
            arguments={
                "url": "https://site.com/1",
                "max_pages": 3,
                "pagination": "next_link",
            },
        ),
    )

    assert result.success
    assert result.output["page_count"] == 3


@pytest.mark.asyncio
async def test_url_pattern_pagination_requires_template() -> None:
    sessions = BrowserSessionManager(
        provider=ScriptedBrowserProvider(pages=_pages(1)),
    )
    tool = ScrapeTool(sessions=sessions)

    result = await tool.execute(
        ToolContext(
            arguments={
                "url": "https://site.com/1",
                "pagination": "url_pattern",
            },
        ),
    )

    assert not result.success
    assert "url_template" in result.error


@pytest.mark.asyncio
async def test_rejects_unknown_pagination_mode() -> None:
    sessions = BrowserSessionManager(
        provider=ScriptedBrowserProvider(pages=_pages(1)),
    )
    tool = ScrapeTool(sessions=sessions)

    result = await tool.execute(
        ToolContext(
            arguments={
                "url": "https://site.com/1",
                "pagination": "infinite_scroll",
            },
        ),
    )

    assert not result.success


@pytest.mark.asyncio
async def test_rejects_non_integer_max_pages() -> None:
    sessions = BrowserSessionManager(
        provider=ScriptedBrowserProvider(pages=_pages(1)),
    )
    tool = ScrapeTool(sessions=sessions)

    result = await tool.execute(
        ToolContext(
            arguments={
                "url": "https://site.com/1",
                "max_pages": "many",
            },
        ),
    )

    assert not result.success
