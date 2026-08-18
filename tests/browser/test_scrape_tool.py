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
        pages[url] = {
            "structured": {"title": f"Page {i}"},
            "links": (
                [{"href": next_url, "text": "Next", "rel": "next"}]
                if next_url
                else []
            ),
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
async def test_multi_page_scrape_defaults_to_next_link() -> None:
    sessions = BrowserSessionManager(
        provider=ScriptedBrowserProvider(pages=_pages(3)),
    )
    tool = ScrapeTool(sessions=sessions)

    result = await tool.execute(
        ToolContext(
            arguments={
                "url": "https://site.com/1",
                "max_pages": 3,
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
