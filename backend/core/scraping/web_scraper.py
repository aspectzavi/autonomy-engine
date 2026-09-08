"""
Web scraper.

Deterministic multi-page crawl orchestrator: given a start URL and an
optional pagination strategy, visits pages one at a time, extracts a
generic structured summary of each (title, headings, text, links,
images, tables), and stops on max_pages, a missing next page, a
repeated URL (cycle detection), an empty follow-up page, or a page
that fails to load.

No LLM call happens anywhere in this loop -- an agent decides once
what to scrape (a URL, a pagination strategy, how many pages) and this
class carries the entire multi-page crawl out deterministically. This
is what keeps per-page cost at zero regardless of how many pages a
scrape needs to cover.
"""

from __future__ import annotations

import asyncio
from urllib.parse import urlsplit, urlunsplit

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


def _normalize_url(url: str) -> str:
    """
    Normalize a URL for cycle detection.

    Strips fragments and a trailing slash on the path (except root)
    so ``/smartphones`` and ``/smartphones/`` count as the same page.
    """
    parts = urlsplit(url.strip())
    path = parts.path or "/"
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")
    return urlunsplit(
        (parts.scheme.casefold(), parts.netloc.casefold(), path, parts.query, ""),
    )


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
        previous_link_count: int | None = None

        for page_number in range(1, max_pages + 1):
            if url is None:
                break

            normalized = _normalize_url(url)

            if normalized in visited:
                # Cycle / redirect back to an already-seen page.
                break

            visited.add(normalized)

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

            # Prefer the post-navigation URL (handles redirects).
            landed_url = getattr(session, "url", None) or url
            landed_normalized = _normalize_url(str(landed_url))

            if (
                landed_normalized != normalized
                and landed_normalized in visited
            ):
                # Redirected into a page we already scraped.
                break

            if landed_normalized not in visited:
                visited.add(landed_normalized)

            extract_result = (
                await self._provider.extract_structured(
                    session,
                )
            )

            if not extract_result.success:
                pages.append(
                    ScrapedPage.failed(
                        str(landed_url),
                        extract_result.error
                        or "Extraction failed.",
                    ),
                )
                break

            structured = extract_result.output

            if not isinstance(structured, dict):
                pages.append(
                    ScrapedPage.failed(
                        str(landed_url),
                        "Extraction returned unexpected data.",
                    ),
                )
                break

            page = ScrapedPage.from_structured(
                str(landed_url),
                structured,
            )
            pages.append(page)

            link_count = len(page.links) if page.links else 0
            text_length = len(page.text.strip()) if page.text else 0

            # After page 1: stop if the page looks like an empty
            # past-the-end shell -- both no links AND barely any
            # text. Checking links alone is too easily wrong: a real
            # listing page can legitimately have zero anchor-style
            # links (e.g. cards rendered without <a> tags) while
            # still holding real content, especially with
            # UrlPatternPaginationStrategy, which computes the next
            # URL from a template regardless of what's on the page.
            if (
                page_number > 1
                and link_count == 0
                and text_length < 40
            ):
                break

            if (
                page_number > 1
                and previous_link_count is not None
                and link_count > 0
                and link_count == previous_link_count
                and _normalize_url(str(landed_url))
                == _normalize_url(pages[-2].url)
            ):
                # Same URL content twice -- nothing new.
                break

            previous_link_count = link_count

            reached_page_limit = page_number == max_pages

            if pagination is None or reached_page_limit:
                break

            if delay_seconds > 0:
                await asyncio.sleep(delay_seconds)

            url = await pagination.next_url(
                provider=self._provider,
                session=session,
                current_url=str(landed_url),
                page_number=page_number,
            )

        return pages