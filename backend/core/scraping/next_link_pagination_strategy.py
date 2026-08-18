"""
Next-link pagination strategy.

Finds a "next page" link generically -- by rel="next", or by link
text matching common patterns ("next", "next page", "older posts",
">", raquo/chevron characters) -- so it works across sites without
needing a site-specific selector.
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

_DEFAULT_TEXT_PATTERNS = (
    "next",
    "next page",
    "older",
    "older posts",
    ">",
    "»",
    "\u203a",
)


class NextLinkPaginationStrategy(PaginationStrategy):
    """
    Follows a "next page" link found on the current page.
    """

    def __init__(
        self,
        *,
        text_patterns: tuple[str, ...] = _DEFAULT_TEXT_PATTERNS,
    ) -> None:
        self._text_patterns = tuple(
            pattern.casefold()
            for pattern in text_patterns
        )

    async def next_url(
        self,
        *,
        provider: "BrowserProvider",
        session: "BrowserSession",
        current_url: str,
        page_number: int,
    ) -> str | None:
        result = await provider.extract_links(session)

        if not result.success:
            return None

        links: list[dict[str, object]] = (
            result.output  # type: ignore[assignment]
            or []
        )

        #
        # Prefer an explicit rel="next" link -- unambiguous when
        # present, before falling back to text matching.
        #
        for link in links:
            rel = str(link.get("rel") or "").casefold()

            if "next" in rel.split():
                return str(link.get("href"))

        for link in links:
            text = str(
                link.get("text") or "",
            ).strip().casefold()

            if text in self._text_patterns:
                return str(link.get("href"))

        return None
