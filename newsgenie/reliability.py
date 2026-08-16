from __future__ import annotations

from urllib.parse import urlparse

# A lightweight provenance indicator, not an automated truth verdict.
TIER_1_DOMAINS = {
    "reuters.com", "apnews.com", "bbc.com", "bbc.co.uk", "npr.org",
    "ft.com", "bloomberg.com", "wsj.com", "nytimes.com", "washingtonpost.com",
}
TIER_2_DOMAINS = {
    "cnn.com", "cnbc.com", "forbes.com", "espn.com", "theguardian.com",
    "techcrunch.com", "theverge.com", "arstechnica.com", "marketwatch.com",
}


def canonical_domain(url: str) -> str:
    try:
        host = urlparse(url).netloc.lower().split(":")[0]
    except Exception:
        return ""
    if host.startswith("www."):
        host = host[4:]
    return host


def reliability_tier(url: str, source_name: str = "") -> str:
    domain = canonical_domain(url)
    if any(domain == d or domain.endswith("." + d) for d in TIER_1_DOMAINS):
        return "Tier 1 - highly established"
    if any(domain == d or domain.endswith("." + d) for d in TIER_2_DOMAINS):
        return "Tier 2 - established"
    if source_name:
        return "Tier 3 - verify source"
    return "Unrated"
