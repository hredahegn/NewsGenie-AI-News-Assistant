from datetime import datetime, timedelta, timezone
from email.utils import format_datetime

from newsgenie.llm import LLMService
from newsgenie.models import NewsItem
from newsgenie.news_service import _current_items
from newsgenie.reliability import reliability_tier


def test_rule_based_news_routing():
    llm = LLMService(api_key=None)
    result = llm.classify("Give me the latest technology news")
    assert result == {"route": "news", "category": "technology"}


def test_rule_based_politics_routing():
    llm = LLMService(api_key=None)
    result = llm.classify("Give me the latest politics news")
    assert result == {"route": "news", "category": "politics"}


def test_rule_based_general_routing():
    llm = LLMService(api_key=None)
    result = llm.classify("Explain what a large language model is")
    assert result["route"] == "general"


def test_source_tier():
    assert reliability_tier("https://www.reuters.com/example").startswith("Tier 1")


def test_live_news_excludes_stale_items_and_sorts_newest_first():
    now = datetime.now(timezone.utc)
    fresh_new = NewsItem(
        title="Newest",
        url="https://example.com/newest",
        source="Example",
        published_at=(now - timedelta(minutes=5)).isoformat(),
    )
    fresh_old = NewsItem(
        title="Older but current",
        url="https://example.com/current",
        source="Example",
        published_at=format_datetime(now - timedelta(hours=5)),
    )
    stale = NewsItem(
        title="Stale",
        url="https://example.com/stale",
        source="Example",
        published_at=(now - timedelta(days=10)).isoformat(),
    )

    result = _current_items([stale, fresh_old, fresh_new], limit=8)
    assert [item.title for item in result] == ["Newest", "Older but current"]
