"""
Web scraper.

Deterministic multi-page crawl orchestrator: given a start URL and an
optional pagination strategy, visits pages one at a time, extracts a
generic structured summary of each (title, headings, text, links,
images, tables), and stops on max_pages, a missing next page, a
repeated URL (cycle detection), or a page that fails to load.

No LLM call happens anywhere in this loop -- an agent decides once
what to scrape (a URL, a pagination strategy, how many pages) and this
class carries the entire multi-page crawl out deterministically. This
is what keeps per-page cost at zero regardless of how many pages a
scrape needs to cover.
"""

from __future__ import annotations

import asyncio

from backend.core.providers.browser.browser_provider import (
    BrowserProvider,
)
from backend.core.providers.browser.browser_session import (
    BrowserSession,
)
from backend.core.scraping.pagination_strategy import (
    PaginationStrategy,
)
from backend.core.scraping.scraped_page import ScrapedPage


class WebScraper:
    """
    Deterministic multi-page web scraper.
    """

    def __init__(
        self,
        *,
        provider: BrowserProvider,
    ) -> None:
        self._provider = provider

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def provider(
        self,
    ) -> BrowserProvider:
        """
        The browser provider this scraper drives.
        """

        return self._provider

    # ------------------------------------------------------------------
    # Crawl
    # ------------------------------------------------------------------

    async def scrape(
        self,
        start_url: str,
        *,
        session: BrowserSession | None = None,
        pagination: PaginationStrategy | None = None,
        max_pages: int = 1,
        delay_seconds: float = 0.0,
    ) -> list[ScrapedPage]:
        """
        Crawl starting at `start_url`, following `pagination` (if
        given) up to `max_pages` pages.

        A single page is scraped if `pagination` is None or
        `max_pages` is 1. `delay_seconds` adds a pause between page
        loads, useful for sites sensitive to rapid requests.

        A session is opened and closed for the duration of this call
        if one isn't supplied, so callers doing a one-off scrape don't
        need to manage session lifecycle themselves.
        """

        if max_pages < 1:
            raise ValueError(
                "max_pages must be at least 1.",
            )

        owns_session = session is None

        active_session = (
            session
            if session is not None
            else await self._provider.create_session()
        )

        try:
            return await self._crawl(
                start_url,
                session=active_session,
                pagination=pagination,
                max_pages=max_pages,
                delay_seconds=delay_seconds,
            )
        finally:
            if owns_session:
                await self._provider.close_session(
                    active_session,
                )

    async def _crawl(
        self,
        start_url: str,
        *,
        session: BrowserSession,
        pagination: PaginationStrategy | None,
        max_pages: int,
        delay_seconds: float,
    ) -> list[ScrapedPage]:
        pages: list[ScrapedPage] = []
        visited: set[str] = set()

        url: str | None = start_url

        for page_number in range(1, max_pages + 1):
            if url is None:
                break

            if url in visited:
                #
                # Cycle detected (pagination looped back to an
                # already-visited page) -- stop rather than crawl
                # forever.
                #
                break

            visited.add(url)

            nav_result = await self._provider.navigate(
                session,
                url,
            )

            if not nav_result.success:
                pages.append(
                    ScrapedPage.failed(
                        url,
                        nav_result.error
                        or "Navigation failed.",
                    ),
                )
                break

            extract_result = (
                await self._provider.extract_structured(
                    session,
                )
            )

            if not extract_result.success:
                pages.append(
                    ScrapedPage.failed(
                        url,
                        extract_result.error
                        or "Extraction failed.",
                    ),
                )
                break

            structured = extract_result.output

            if not isinstance(structured, dict):
                pages.append(
                    ScrapedPage.failed(
                        url,
                        "Extraction returned unexpected data.",
                    ),
                )
                break

            pages.append(
                ScrapedPage.from_structured(
                    url,
                    structured,
                ),
            )

            reached_page_limit = (
                page_number == max_pages
            )

            if pagination is None or reached_page_limit:
                break

            if delay_seconds > 0:
                await asyncio.sleep(delay_seconds)

            url = await pagination.next_url(
                provider=self._provider,
                session=session,
                current_url=url,
                page_number=page_number,
            )

        return pages
