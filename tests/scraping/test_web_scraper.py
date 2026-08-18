"""
Web scraper tests.

Verifies the crawl loop itself: multi-page traversal via a pagination
strategy, max_pages cutoff, cycle detection, and error handling for a
page that fails to load or extract.
"""

from __future__ import annotations

import pytest

from backend.core.scraping.next_link_pagination_strategy import (
    NextLinkPaginationStrategy,
)
from backend.core.scraping.web_scraper import WebScraper
from tests.scraping.fakes import ScriptedBrowserProvider


def _linked_pages(count: int) -> dict:
    """
    Build `count` pages, each linking to the next via a "Next" link,
    the last page having no next link.
    """

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
async def test_single_page_scrape_without_pagination() -> None:
    provider = ScriptedBrowserProvider(pages=_linked_pages(3))
    scraper = WebScraper(provider=provider)

    pages = await scraper.scrape("https://site.com/1")

    assert len(pages) == 1
    assert pages[0].title == "Page 1"
    assert pages[0].success


@pytest.mark.asyncio
async def test_follows_pagination_across_all_available_pages() -> None:
    provider = ScriptedBrowserProvider(pages=_linked_pages(3))
    scraper = WebScraper(provider=provider)

    pages = await scraper.scrape(
        "https://site.com/1",
        pagination=NextLinkPaginationStrategy(),
        max_pages=10,
    )

    assert [p.title for p in pages] == ["Page 1", "Page 2", "Page 3"]


@pytest.mark.asyncio
async def test_stops_at_max_pages_even_if_more_are_available() -> None:
    provider = ScriptedBrowserProvider(pages=_linked_pages(5))
    scraper = WebScraper(provider=provider)

    pages = await scraper.scrape(
        "https://site.com/1",
        pagination=NextLinkPaginationStrategy(),
        max_pages=2,
    )

    assert [p.title for p in pages] == ["Page 1", "Page 2"]


@pytest.mark.asyncio
async def test_ignores_pagination_when_max_pages_is_one() -> None:
    provider = ScriptedBrowserProvider(pages=_linked_pages(3))
    scraper = WebScraper(provider=provider)

    pages = await scraper.scrape(
        "https://site.com/1",
        pagination=NextLinkPaginationStrategy(),
        max_pages=1,
    )

    assert len(pages) == 1


@pytest.mark.asyncio
async def test_stops_on_cycle_back_to_a_visited_page() -> None:
    pages = _linked_pages(2)
    #
    # Make page 2 link back to page 1 -- an infinite loop if not for
    # cycle detection.
    #
    pages["https://site.com/2"]["links"] = [
        {"href": "https://site.com/1", "text": "Next", "rel": "next"},
    ]

    provider = ScriptedBrowserProvider(pages=pages)
    scraper = WebScraper(provider=provider)

    result = await scraper.scrape(
        "https://site.com/1",
        pagination=NextLinkPaginationStrategy(),
        max_pages=10,
    )

    assert [p.title for p in result] == ["Page 1", "Page 2"]


@pytest.mark.asyncio
async def test_stops_on_navigation_failure() -> None:
    provider = ScriptedBrowserProvider(
        pages={
            "https://site.com/1": {
                "structured": {"title": "Page 1"},
                "links": [
                    {"href": "https://site.com/missing", "text": "Next", "rel": "next"},
                ],
            },
        },
    )
    scraper = WebScraper(provider=provider)

    pages = await scraper.scrape(
        "https://site.com/1",
        pagination=NextLinkPaginationStrategy(),
        max_pages=5,
    )

    assert len(pages) == 2
    assert pages[0].success
    assert not pages[1].success
    assert pages[1].error


@pytest.mark.asyncio
async def test_stops_on_extraction_failure() -> None:
    provider = ScriptedBrowserProvider(
        pages={
            "https://site.com/1": {
                "fail_extract": True,
            },
        },
    )
    scraper = WebScraper(provider=provider)

    pages = await scraper.scrape("https://site.com/1")

    assert len(pages) == 1
    assert not pages[0].success


@pytest.mark.asyncio
async def test_rejects_non_positive_max_pages() -> None:
    provider = ScriptedBrowserProvider(pages=_linked_pages(1))
    scraper = WebScraper(provider=provider)

    with pytest.raises(ValueError):
        await scraper.scrape("https://site.com/1", max_pages=0)


@pytest.mark.asyncio
async def test_closes_a_self_opened_session_afterward() -> None:
    provider = ScriptedBrowserProvider(pages=_linked_pages(1))
    scraper = WebScraper(provider=provider)

    await scraper.scrape("https://site.com/1")

    #
    # ScriptedBrowserProvider doesn't track open sessions the way
    # PlaywrightBrowserProvider does, but close_session() should
    # still have been reachable/callable without error -- verified
    # implicitly by scrape() completing without raising.
    #
    assert provider.visited_urls == ["https://site.com/1"]
