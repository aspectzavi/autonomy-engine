"""
Scraped page.

Result of scraping a single page during a crawl.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class ScrapedPage:
    """
    Structured data extracted from one page during a crawl.
    """

    url: str

    success: bool = True

    error: str | None = None

    title: str | None = None

    meta_description: str | None = None

    headings: tuple[dict[str, object], ...] = field(
        default_factory=tuple,
    )

    text: str = ""

    links: tuple[dict[str, object], ...] = field(
        default_factory=tuple,
    )

    images: tuple[dict[str, object], ...] = field(
        default_factory=tuple,
    )

    tables: tuple[list[list[str]], ...] = field(
        default_factory=tuple,
    )

    # ------------------------------------------------------------------
    # Constructors
    # ------------------------------------------------------------------

    @classmethod
    def from_structured(
        cls,
        url: str,
        data: dict[str, object],
    ) -> "ScrapedPage":
        """
        Build a ScrapedPage from a BrowserProvider.extract_structured()
        output.
        """

        return cls(
            url=url,
            title=data.get("title"),  # type: ignore[arg-type]
            meta_description=data.get(
                "meta_description",
            ),  # type: ignore[arg-type]
            headings=tuple(
                data.get("headings", []),  # type: ignore[arg-type]
            ),
            text=data.get("text", ""),  # type: ignore[arg-type]
            links=tuple(
                data.get("links", []),  # type: ignore[arg-type]
            ),
            images=tuple(
                data.get("images", []),  # type: ignore[arg-type]
            ),
            tables=tuple(
                data.get("tables", []),  # type: ignore[arg-type]
            ),
        )

    @classmethod
    def failed(
        cls,
        url: str,
        error: str,
    ) -> "ScrapedPage":
        """
        Build a ScrapedPage representing a page that failed to load
        or extract.
        """

        return cls(
            url=url,
            success=False,
            error=error,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return page diagnostics.
        """

        return {
            "url": self.url,
            "success": self.success,
            "error": self.error,
            "title": self.title,
            "heading_count": len(self.headings),
            "link_count": len(self.links),
            "image_count": len(self.images),
            "table_count": len(self.tables),
            "text_length": len(self.text),
        }
