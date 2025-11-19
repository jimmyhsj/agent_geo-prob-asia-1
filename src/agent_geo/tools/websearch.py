from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List, Optional

from agent_geo.models.evidence import EvidenceRecord

try:  # pragma: no cover - optional dependency import guard
    from duckduckgo_search import DDGS
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "duckduckgo-search is required for WebSearchTool. Install via `pip install duckduckgo-search`."
    ) from exc


@dataclass(slots=True)
class WebSearchResult:
    title: str
    url: str
    snippet: str
    published: Optional[datetime] = None
    source: Optional[str] = None


class WebSearchTool:
    def __init__(
        self,
        *,
        region: str = "jp-jp",
        safesearch: str = "moderate",
        max_results: int = 5,
    ) -> None:
        self.region = region
        self.safesearch = safesearch
        self.max_results = max_results
        self._client = DDGS()

    def search(self, query: str) -> List[WebSearchResult]:
        raw_results = self._client.text(
            query,
            region=self.region,
            safesearch=self.safesearch,
            max_results=self.max_results,
        )
        results: List[WebSearchResult] = []
        for item in raw_results:
            published = None
            if item.get("date"):
                try:
                    published = datetime.fromisoformat(item["date"])
                except ValueError:
                    published = None
            results.append(
                WebSearchResult(
                    title=item.get("title") or query,
                    url=item.get("href") or item.get("url") or "",
                    snippet=item.get("body") or "",
                    published=published,
                    source=item.get("source"),
                )
            )
        return results

    @staticmethod
    def to_evidence(
        result: WebSearchResult,
        *,
        quality: str = "M",
        quote: Optional[str] = None,
    ) -> EvidenceRecord:
        return EvidenceRecord(
            title=result.title,
            date=result.published,
            source=result.source or "websearch",
            quote=quote or result.snippet[:240],
            url=result.url,
            quality=quality,
        )

    def search_as_evidence(self, query: str, *, quality: str = "M") -> List[EvidenceRecord]:
        return [self.to_evidence(result, quality=quality) for result in self.search(query) if result.url]


__all__ = ["WebSearchTool", "WebSearchResult"]
