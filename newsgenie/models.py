from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class NewsItem:
    title: str
    url: str
    source: str
    published_at: str = ""
    description: str = ""
    reliability_tier: str = "Unrated"
    retrieval_method: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SearchItem:
    title: str
    url: str
    snippet: str
    retrieval_method: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
