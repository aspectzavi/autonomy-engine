"""
Pagination strategy.

Abstraction for how a crawl decides which URL to visit next. Kept
separate from WebScraper so "any site" scraping can plug in whichever
strategy actually matches that site's pagination scheme (a "Next"
link, a numbered URL pattern, infinite scroll, etc.) without WebScraper
needing to know the details.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.core.providers.browser.browser_provider import (
        BrowserProvider,
    )
    from backend.core.providers.browser.browser_session import (
        BrowserSession,
    )


class PaginationStrategy(ABC):
    """
    Decides the next URL to visit during a multi-page crawl.
    """

    @abstractmethod
    async def next_url(
        self,
        *,
        provider: "BrowserProvider",
        session: "BrowserSession",
        current_url: str,
        page_number: int,
    ) -> str | None:
        """
        Return the next URL to visit, or None if there is no next
        page (the crawl should stop).

        Called after the current page has already been navigated to
        and extracted, so implementations may inspect the live page
        (e.g. via provider.extract_links()) to find a "next" link.
        """
