from __future__ import annotations

import os
import requests

from .models import SearchItem


class WebSearchService:
    """Tavily web search with DDGS as an optional key-free fallback."""

    def __init__(self, tavily_api_key: str | None = None, timeout: int = 10):
        self.tavily_api_key = tavily_api_key or os.getenv("TAVILY_API_KEY")
        self.timeout = timeout

    def search(self, query: str, limit: int = 5) -> tuple[list[SearchItem], str]:
        if self.tavily_api_key:
            try:
                results = self._tavily(query, limit)
                if results:
                    return results, "Tavily"
            except Exception:
                pass
        try:
            results = self._ddgs(query, limit)
            if results:
                return results, "DDGS fallback"
        except Exception:
            pass
        return [], "No web-search source available"

    def _tavily(self, query: str, limit: int) -> list[SearchItem]:
        response = requests.post(
            "https://api.tavily.com/search",
            headers={"Authorization": f"Bearer {self.tavily_api_key}", "Content-Type": "application/json"},
            json={
                "query": query,
                "search_depth": "basic",
                "max_results": min(limit, 10),
                "include_answer": False,
                "include_raw_content": False,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        return [
            SearchItem(
                title=r.get("title") or "Untitled",
                url=r.get("url") or "",
                snippet=r.get("content") or "",
                retrieval_method="Tavily",
            )
            for r in payload.get("results", [])
        ]

    def _ddgs(self, query: str, limit: int) -> list[SearchItem]:
        from ddgs import DDGS

        raw = DDGS(timeout=self.timeout).text(query, max_results=limit)
        return [
            SearchItem(
                title=r.get("title") or "Untitled",
                url=r.get("href") or r.get("url") or "",
                snippet=r.get("body") or r.get("snippet") or "",
                retrieval_method="DDGS fallback",
            )
            for r in (raw or [])
        ]
