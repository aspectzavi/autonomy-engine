"""
Scrape tool.

Crawls one or more pages starting at a URL and returns structured
data for each. This is a single tool call that can cover an entire
multi-page site -- the crawl loop runs entirely in WebScraper with no
further LLM involvement per page, which is the point: an agent pays
for one decision ("scrape this site, up to N pages") instead of one
decision per page.

Works on any site out of the box (extraction is generic DOM parsing,
not site-specific selectors). Two pagination modes:

- "next_link" (default): follows a rel="next" or "Next"-labelled link
  found on each page -- works on most blogs, docs sites, and paginated
  listings without any per-site configuration.
- "url_pattern": generates page URLs from a `{page}` template
  (e.g. "https://example.com/articles?page={page}") for sites whose
  pagination is a predictable URL scheme rather than a clickable link.
"""

from __future__ import annotations

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
                "single call. Works on any site."
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

        pagination_mode = context.argument(
            "pagination",
            "next_link" if max_pages > 1 else None,
        )

        pagination: PaginationStrategy | None = None

        if pagination_mode == "next_link":
            pagination = NextLinkPaginationStrategy()

        elif pagination_mode == "url_pattern":
            url_template = context.argument("url_template")

            if not isinstance(url_template, str) or not url_template:
                return self.missing_argument(
                    "url_template",
                    started_at=started_at,
                )

            try:
                pagination = UrlPatternPaginationStrategy(
                    url_template=url_template,
                )
            except ValueError as exc:
                return ToolResult.failure(
                    error=str(exc),
                    started_at=started_at,
                )

        elif pagination_mode not in (None, "none"):
            return ToolResult.failure(
                error=(
                    "'pagination' must be one of: 'next_link', "
                    "'url_pattern', or omitted."
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
