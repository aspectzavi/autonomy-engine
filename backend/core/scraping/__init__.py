"""
Scraping subsystem.

Deterministic, Playwright-backed multi-page web scraping: given a
start URL and a pagination strategy, crawls and extracts structured
data from every page it visits without any LLM call per page. An
agent decides once what to scrape; WebScraper carries the crawl out.
"""

from backend.core.scraping.next_link_pagination_strategy import (
    NextLinkPaginationStrategy,
)
from backend.core.scraping.pagination_strategy import (
    PaginationStrategy,
)
from backend.core.scraping.scraped_page import ScrapedPage
from backend.core.scraping.url_pattern_pagination_strategy import (
    UrlPatternPaginationStrategy,
)
from backend.core.scraping.web_scraper import WebScraper

__all__ = [
    "NextLinkPaginationStrategy",
    "PaginationStrategy",
    "ScrapedPage",
    "UrlPatternPaginationStrategy",
    "WebScraper",
]
