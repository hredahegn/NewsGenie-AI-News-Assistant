from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Iterable
from urllib.parse import quote_plus

import requests

from .models import NewsItem
from .reliability import reliability_tier

CATEGORY_MAP = {
    "technology": "technology",
    "finance": "business",
    "sports": "sports",
    "politics": "general",
    "general": "general",
}

RSS_QUERY_MAP = {
    "technology": "technology AI software chips",
    "finance": "finance markets economy stocks",
    "sports": "sports",
    "politics": "politics government elections congress White House",
    "general": "top news",
}


def _dedupe(items: Iterable[NewsItem], limit: int = 8) -> list[NewsItem]:
    seen: set[str] = set()
    output: list[NewsItem] = []
    for item in items:
        key = " ".join(item.title.lower().split())
        if not key or key in seen:
            continue
        seen.add(key)
        output.append(item)
        if len(output) >= limit:
            break
    return output


class NewsService:
    """Primary NewsAPI integration with a key-free Google News RSS fallback."""

    def __init__(self, api_key: str | None = None, country: str = "us", timeout: int = 10):
        self.api_key = api_key or os.getenv("NEWSAPI_KEY")
        self.country = country
        self.timeout = timeout

    def fetch(self, category: str, query: str = "", limit: int = 8) -> tuple[list[NewsItem], str]:
        category = category.lower().strip() if category else "general"
        if self.api_key:
            try:
                items = self._newsapi(category, query, limit)
                if items:
                    return _dedupe(items, limit), "NewsAPI"
            except Exception:
                pass

        try:
            items = self._google_news_rss(category, query, limit)
            if items:
                return _dedupe(items, limit), "Google News RSS fallback"
        except Exception:
            pass
        return [], "No source available"

    def _newsapi(self, category: str, query: str, limit: int) -> list[NewsItem]:
        endpoint = "https://newsapi.org/v2/top-headlines"
        params = {
            "apiKey": self.api_key,
            "country": self.country,
            "category": CATEGORY_MAP.get(category, "general"),
            "pageSize": min(limit, 20),
        }
        if query:
            params["q"] = query[:200]
        elif category == "politics":
            params["q"] = "politics government elections congress White House"
        response = requests.get(endpoint, params=params, timeout=self.timeout)
        response.raise_for_status()
        payload = response.json()
        if payload.get("status") != "ok":
            raise RuntimeError(payload.get("message", "NewsAPI returned an error"))
        items: list[NewsItem] = []
        for article in payload.get("articles", []):
            url = article.get("url") or ""
            source = (article.get("source") or {}).get("name") or "Unknown"
            items.append(
                NewsItem(
                    title=article.get("title") or "Untitled",
                    url=url,
                    source=source,
                    published_at=article.get("publishedAt") or "",
                    description=article.get("description") or "",
                    reliability_tier=reliability_tier(url, source),
                    retrieval_method="NewsAPI",
                )
            )
        return items

    def _google_news_rss(self, category: str, query: str, limit: int) -> list[NewsItem]:
        import xml.etree.ElementTree as ET

        q = query.strip() or RSS_QUERY_MAP.get(category, category)
        rss_url = (
            "https://news.google.com/rss/search?q=" + quote_plus(q)
            + "&hl=en-US&gl=US&ceid=US:en"
        )
        response = requests.get(rss_url, timeout=self.timeout, headers={"User-Agent": "NewsGenie/1.0"})
        response.raise_for_status()
        root = ET.fromstring(response.content)
        items: list[NewsItem] = []
        for node in root.findall("./channel/item")[:limit]:
            title = (node.findtext("title") or "Untitled").strip()
            link = (node.findtext("link") or "").strip()
            pub_date = (node.findtext("pubDate") or "").strip()
            source_node = node.find("source")
            source = (source_node.text or "Google News") if source_node is not None else "Google News"
            items.append(
                NewsItem(
                    title=title,
                    url=link,
                    source=source,
                    published_at=pub_date,
                    description="Retrieved from the Google News RSS index.",
                    reliability_tier=reliability_tier(link, source),
                    retrieval_method="Google News RSS fallback",
                )
            )
        return items

    @staticmethod
    def freshness_label(published_at: str) -> str:
        if not published_at:
            return "time unavailable"
        try:
            dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
            age = datetime.now(timezone.utc) - dt.astimezone(timezone.utc)
            hours = max(age.total_seconds() / 3600, 0)
            if hours < 1:
                return "<1 hour ago"
            if hours < 24:
                return f"{hours:.0f} hours ago"
            return f"{hours / 24:.0f} days ago"
        except Exception:
            return published_at
