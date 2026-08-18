"""
URL-pattern pagination strategy.

Generates the next page URL by substituting an incrementing page
number into a template, for sites whose pagination is a predictable
URL scheme (e.g. "https://example.com/articles?page={page}") rather
than a clickable "next" link.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from backend.core.scraping.pagination_strategy import (
    PaginationStrategy,
)

if TYPE_CHECKING:
    from backend.core.providers.browser.browser_provider import (
        BrowserProvider,
    )
    from backend.core.providers.browser.browser_session import (
        BrowserSession,
    )


class UrlPatternPaginationStrategy(PaginationStrategy):
    """
    Generates page URLs from a `{page}` template.
    """

    def __init__(
        self,
        *,
        url_template: str,
        start_page: int = 1,
    ) -> None:
        if "{page}" not in url_template:
            raise ValueError(
                "url_template must contain a '{page}' placeholder.",
            )

        self._url_template = url_template
        self._start_page = start_page

    async def next_url(
        self,
        *,
        provider: "BrowserProvider",
        session: "BrowserSession",
        current_url: str,
        page_number: int,
    ) -> str | None:
        next_page_number = (
            self._start_page + page_number
        )

        return self._url_template.format(
            page=next_page_number,
        )
