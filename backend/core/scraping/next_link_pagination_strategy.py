"""
Next-link pagination strategy.

Finds a "next page" link generically so multi-page crawls work without
site-specific selectors.

Resolution order:
1. ``rel="next"`` (unambiguous when present)
2. Exact link text match ("next", ">", "»", …)
3. Partial / aria-label match (text or aria contains "next", "siguiente", …)
4. Query-param page links (``?page=N`` / ``&page=N``) with N = current + 1
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING
from urllib.parse import parse_qs, urljoin, urlsplit

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
    "›",
)

# Substrings allowed inside longer labels (e.g. "Next page →").
_DEFAULT_CONTAINS_PATTERNS = (
    "next",
    "siguiente",  # ES
    "suivant",    # FR
    "weiter",     # DE
    "próxima",    # PT
    "older",
)

_PAGE_QUERY_RE = re.compile(
    r"[?&]page=(\d+)\b",
    re.IGNORECASE,
)


def _link_label(link: dict[str, object]) -> str:
    text = str(link.get("text") or "").strip()
    aria = str(
        link.get("aria_label")
        or link.get("aria-label")
        or "",
    ).strip()
    title = str(link.get("title") or "").strip()
    return " ".join(
        part for part in (text, aria, title) if part
    ).casefold()


def _current_page_number(current_url: str, page_number: int) -> int:
    """
    Prefer ``page`` from the URL query; fall back to the crawl index.
    """
    query = parse_qs(urlsplit(current_url).query)
    raw = query.get("page") or query.get("p")
    if raw:
        try:
            return int(raw[0])
        except (TypeError, ValueError):
            pass
    return page_number


class NextLinkPaginationStrategy(PaginationStrategy):
    """
    Follows a "next page" link found on the current page.
    """

    def __init__(
        self,
        *,
        text_patterns: tuple[str, ...] = _DEFAULT_TEXT_PATTERNS,
        contains_patterns: tuple[str, ...] = _DEFAULT_CONTAINS_PATTERNS,
    ) -> None:
        self._text_patterns = tuple(
            pattern.casefold()
            for pattern in text_patterns
        )
        self._contains_patterns = tuple(
            pattern.casefold()
            for pattern in contains_patterns
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

        if not links:
            return None

        # Absolute hrefs relative to the page we are on.
        resolved: list[tuple[dict[str, object], str]] = []
        for link in links:
            href = str(link.get("href") or "").strip()
            if not href or href.startswith(("#", "javascript:", "mailto:")):
                continue
            resolved.append((link, urljoin(current_url, href)))

        #
        # 1) rel="next"
        #
        for link, href in resolved:
            rel = str(link.get("rel") or "").casefold()
            if "next" in rel.split():
                return href

        #
        # 2) Exact text match
        #
        for link, href in resolved:
            text = str(link.get("text") or "").strip().casefold()
            if text in self._text_patterns:
                return href

        #
        # 3) Partial text / aria-label / title
        #
        for link, href in resolved:
            label = _link_label(link)
            if not label:
                continue
            for pattern in self._contains_patterns:
                if pattern in label:
                    return href

        #
        # 4) ?page=N (or &page=N) where N == current + 1
        #
        current_page = _current_page_number(current_url, page_number)
        target_page = current_page + 1

        page_candidates: list[str] = []
        for _link, href in resolved:
            match = _PAGE_QUERY_RE.search(href)
            if not match:
                continue
            try:
                n = int(match.group(1))
            except ValueError:
                continue
            if n == target_page:
                page_candidates.append(href)

        if page_candidates:
            # Prefer same path as current URL when several match.
            current_path = urlsplit(current_url).path
            for href in page_candidates:
                if urlsplit(href).path == current_path:
                    return href
            return page_candidates[0]

        return None