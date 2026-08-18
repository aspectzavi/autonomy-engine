"""
URL pattern pagination strategy tests.
"""

from __future__ import annotations

import pytest

from backend.core.scraping.url_pattern_pagination_strategy import (
    UrlPatternPaginationStrategy,
)


def test_rejects_template_without_placeholder() -> None:
    with pytest.raises(ValueError):
        UrlPatternPaginationStrategy(
            url_template="https://example.com/articles",
        )


@pytest.mark.asyncio
async def test_generates_the_next_page_number() -> None:
    strategy = UrlPatternPaginationStrategy(
        url_template="https://example.com/articles?page={page}",
    )

    next_url = await strategy.next_url(
        provider=None,
        session=None,
        current_url="https://example.com/articles?page=1",
        page_number=1,
    )

    assert next_url == "https://example.com/articles?page=2"


@pytest.mark.asyncio
async def test_respects_a_custom_start_page() -> None:
    strategy = UrlPatternPaginationStrategy(
        url_template="https://example.com/p/{page}",
        start_page=0,
    )

    next_url = await strategy.next_url(
        provider=None,
        session=None,
        current_url="https://example.com/p/0",
        page_number=1,
    )

    assert next_url == "https://example.com/p/1"
