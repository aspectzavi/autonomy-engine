"""
Scrape tool.

Crawls one or more pages starting at a URL and returns structured
data for each. This is a single tool call that can cover an entire
multi-page site -- the crawl loop runs entirely in WebScraper with no
further LLM involvement per page, which is the point: an agent pays
for one decision ("scrape this site, up to N pages") instead of one
decision per page.

Works on any site out of the box (extraction is generic DOM parsing,
not site-specific selectors). Pagination modes:

- "auto" (default when max_pages > 1): builds a ``page={page}`` URL
  template from the start URL so sites like Jumia (``?page=2``) work
  without a hand-written template. Falls back cleanly if you pass an
  explicit mode instead.
- "next_link": follows a rel="next" or "Next"-labelled link found on
  each page -- works on many blogs/docs sites.
- "url_pattern": generates page URLs from a caller-supplied ``{page}``
  template (e.g. "https://example.com/articles?page={page}").
"""

from __future__ import annotations

from urllib.parse import (
    parse_qsl,
    urlencode,
    urlsplit,
    urlunsplit,
)

from backend.core.providers.browser.browser_session_manager import (
    BrowserSessionManager,
)
from backend.core.scraping.next_link_pagination_strategy import (
    NextLinkPaginationStrategy,
)
from backend.core.scraping.pagination_strategy import (
    PaginationStrategy,
)
from backend.core.scraping.url_pattern_pagination_strategy import (
    UrlPatternPaginationStrategy,
)
from backend.core.scraping.web_scraper import WebScraper
from backend.core.tools.context import ToolContext
from backend.core.tools.result import ToolResult
from backend.tools.browser.base import BrowserTool


def _infer_page_url_template(url: str) -> str:
    """
    Build a ``{page}`` URL template from a listing URL.

    Examples:
      https://www.jumia.co.ke/smartphones/
        -> https://www.jumia.co.ke/smartphones/?page={page}
      https://example.com/list?sort=new&page=3
        -> https://example.com/list?sort=new&page={page}
    """
    parts = urlsplit(url)
    query_pairs = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if key.casefold() != "page"
    ]
    query_pairs.append(("page", "{page}"))
    # urlencode would escape {page}; keep placeholder literal.
    query = urlencode(query_pairs).replace("%7Bpage%7D", "{page}")
    return urlunsplit(
        (parts.scheme, parts.netloc, parts.path, query, parts.fragment),
    )


class ScrapeTool(BrowserTool):
    """
    Scrape one or more pages, following pagination if requested.
    """

    def __init__(
        self,
        *,
        sessions: BrowserSessionManager,
    ) -> None:
        super().__init__(
            name="browser_scrape",
            description=(
                "Scrape structured data (title, headings, text, "
                "links, images, tables) from a page, optionally "
                "following pagination across multiple pages in a "
                "single call. Works on any site. When max_pages > 1, "
                "defaults to auto page={page} URL pagination."
            ),
            sessions=sessions,
        )
        self._scraper = WebScraper(
            provider=sessions.provider,
        )

    async def execute(
        self,
        context: ToolContext,
    ) -> ToolResult:
        started_at = self.now()

        if context.is_cancelled:
            return ToolResult.failure(
                error="Tool execution was cancelled.",
                started_at=started_at,
            )

        url = context.argument("url")

        if not isinstance(url, str) or not url:
            return self.missing_argument(
                "url",
                started_at=started_at,
            )

        max_pages = context.argument("max_pages", 1)

        try:
            max_pages = int(max_pages)
        except (TypeError, ValueError):
            return ToolResult.failure(
                error="'max_pages' must be an integer.",
                started_at=started_at,
            )

        if max_pages < 1:
            return ToolResult.failure(
                error="'max_pages' must be at least 1.",
                started_at=started_at,
            )

        # Default: single page = no pagination.
        # Multi-page = auto ?page={page} (works for Jumia-style sites).
        # Callers can still force next_link or an explicit url_pattern.
        pagination_mode = context.argument(
            "pagination",
            "auto" if max_pages > 1 else None,
        )

        pagination: PaginationStrategy | None = None

        if pagination_mode in (None, "none"):
            pagination = None

        elif pagination_mode == "next_link":
            pagination = NextLinkPaginationStrategy()

        elif pagination_mode in ("auto", "url_pattern"):
            url_template = context.argument("url_template")

            if not isinstance(url_template, str) or not url_template:
                if pagination_mode == "url_pattern":
                    return self.missing_argument(
                        "url_template",
                        started_at=started_at,
                    )
                # auto: infer from start URL
                url_template = _infer_page_url_template(url)

            try:
                pagination = UrlPatternPaginationStrategy(
                    url_template=url_template,
                )
            except ValueError as exc:
                return ToolResult.failure(
                    error=str(exc),
                    started_at=started_at,
                )

        else:
            return ToolResult.failure(
                error=(
                    "'pagination' must be one of: 'auto', "
                    "'next_link', 'url_pattern', or omitted."
                ),
                started_at=started_at,
            )

        delay_seconds = context.argument("delay_seconds", 0.0)

        try:
            delay_seconds = float(delay_seconds)
        except (TypeError, ValueError):
            return ToolResult.failure(
                error="'delay_seconds' must be a number.",
                started_at=started_at,
            )

        pages = await self._scraper.scrape(
            url,
            pagination=pagination,
            max_pages=max_pages,
            delay_seconds=delay_seconds,
        )

        return ToolResult.ok(
            output={
                "page_count": len(pages),
                "pages": [
                    {
                        "url": page.url,
                        "success": page.success,
                        "error": page.error,
                        "title": page.title,
                        "meta_description": (
                            page.meta_description
                        ),
                        "headings": list(page.headings),
                        "text": page.text,
                        "links": list(page.links),
                        "images": list(page.images),
                        "tables": list(page.tables),
                    }
                    for page in pages
                ],
            },
            started_at=started_at,
        )