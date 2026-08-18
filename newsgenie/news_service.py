from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
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
    "technology": "technology OR AI OR software OR chips",
    "finance": "finance OR markets OR economy OR stocks",
    "sports": "sports",
    "politics": "US politics OR White House OR Congress OR Senate OR elections",
    "general": "top news",
}

# A Live News refresh should never quietly surface weeks-old stories.
# We accept the trailing 24 hours so late-evening stories remain visible after midnight.
LIVE_MAX_AGE_HOURS = 24
RSS_SCAN_LIMIT = 60


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


def _parse_published_at(value: str) -> datetime | None:
    """Parse both NewsAPI ISO timestamps and RSS/RFC-2822 timestamps."""
    if not value:
        return None

    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except (TypeError, ValueError):
        pass

    try:
        dt = parsedate_to_datetime(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except (TypeError, ValueError, OverflowError):
        return None


def _current_items(items: Iterable[NewsItem], limit: int = 8) -> list[NewsItem]:
    """Return only items from the last 24 hours, newest first."""
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=LIVE_MAX_AGE_HOURS)
    future_tolerance = now + timedelta(minutes=10)

    dated: list[tuple[datetime, NewsItem]] = []
    for item in items:
        published = _parse_published_at(item.published_at)
        if published is None:
            # For the Live surface, unknown dates are safer to omit than to present as current.
            continue
        if cutoff <= published <= future_tolerance:
            dated.append((published, item))

    dated.sort(key=lambda pair: pair[0], reverse=True)
    return _dedupe((item for _, item in dated), limit)


class NewsService:
    """Primary NewsAPI integration with a key-free Google News RSS fallback."""

    def __init__(self, api_key: str | None = None, country: str = "us", timeout: int = 10):
        self.api_key = api_key or os.getenv("NEWSAPI_KEY")
        self.country = country
        self.timeout = timeout

    def fetch(self, category: str, query: str = "", limit: int = 8) -> tuple[list[NewsItem], str]:
        """Fetch current stories only and order them by publication time, newest first."""
        category = category.lower().strip() if category else "general"
        candidates: list[NewsItem] = []
        methods: list[str] = []

        if self.api_key:
            try:
                api_items = self._newsapi(category, query, max(limit * 3, 20))
                candidates.extend(api_items)
                if api_items:
                    methods.append("NewsAPI")
            except Exception:
                pass

        # RSS is also queried when NewsAPI works so we can fill the live list with the
        # newest available stories instead of returning a small or relevance-skewed set.
        try:
            rss_items = self._google_news_rss(category, query, RSS_SCAN_LIMIT)
            candidates.extend(rss_items)
            if rss_items:
                methods.append("Google News RSS")
        except Exception:
            pass

        current = _current_items(candidates, limit)
        if current:
            method = " + ".join(methods) if methods else "Current news retrieval"
            return current, f"{method} · newest ≤{LIVE_MAX_AGE_HOURS}h"

        return [], f"No stories published within the last {LIVE_MAX_AGE_HOURS} hours"

    def _newsapi(self, category: str, query: str, limit: int) -> list[NewsItem]:
        endpoint = "https://newsapi.org/v2/top-headlines"
        params = {
            "apiKey": self.api_key,
            "country": self.country,
            "category": CATEGORY_MAP.get(category, "general"),
            "pageSize": min(limit, 100),
        }
        if query:
            params["q"] = query[:200]
        elif category == "politics":
            params["q"] = "politics government congress white house elections"

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

        base_query = query.strip() or RSS_QUERY_MAP.get(category, category)
        # Google News search supports a time-qualified search token. The hard timestamp
        # filter in _current_items remains the source of truth even if the feed ignores it.
        q = base_query if "when:" in base_query.lower() else f"{base_query} when:1d"
        rss_url = (
            "https://news.google.com/rss/search?q=" + quote_plus(q)
            + "&hl=en-US&gl=US&ceid=US:en"
        )
        response = requests.get(
            rss_url,
            timeout=self.timeout,
            headers={"User-Agent": "HaddishSignal/1.0"},
        )
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
                    retrieval_method="Google News RSS",
                )
            )
        return items

    @staticmethod
    def freshness_label(published_at: str) -> str:
        published = _parse_published_at(published_at)
        if published is None:
            return "time unavailable"

        age = datetime.now(timezone.utc) - published
        seconds = max(age.total_seconds(), 0)
        minutes = seconds / 60
        hours = seconds / 3600

        if minutes < 2:
            return "just now"
        if minutes < 60:
            return f"{minutes:.0f} min ago"
        if hours < 24:
            return f"{hours:.0f} hr ago"
        return f"{hours / 24:.0f} days ago"
