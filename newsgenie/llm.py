from __future__ import annotations

import json
import os
import re
from typing import Any


class LLMService:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-5-mini")
        self._llm = None
        if self.api_key:
            try:
                from langchain_openai import ChatOpenAI
                self._llm = ChatOpenAI(
                    model=self.model,
                    api_key=self.api_key,
                    temperature=0.1,
                    max_retries=2,
                )
            except Exception:
                self._llm = None

    @property
    def available(self) -> bool:
        return self._llm is not None

    def classify(self, query: str, history: str = "", selected_category: str = "auto") -> dict[str, str]:
        selected = (selected_category or "auto").lower()
        if selected in {"technology", "finance", "sports", "politics"}:
            return {"route": "news", "category": selected}

        if self.available:
            prompt = f"""
You route requests for NewsGenie. Return ONLY JSON with keys route and category.
route must be either \"news\" or \"general\".
category must be one of \"technology\", \"finance\", \"sports\", \"politics\", \"general\".
Choose news when the user asks for headlines, current events, latest developments, or an update.
Use prior conversation only to resolve follow-ups.

Recent conversation:
{history[-2500:]}

User query: {query}
""".strip()
            try:
                text = self._llm.invoke(prompt).content
                match = re.search(r"\{.*\}", str(text), flags=re.S)
                if match:
                    data = json.loads(match.group(0))
                    route = data.get("route")
                    category = data.get("category")
                    if route in {"news", "general"} and category in {"technology", "finance", "sports", "politics", "general"}:
                        return {"route": route, "category": category}
            except Exception:
                pass

        q = query.lower()
        news_words = {"news", "latest", "headline", "headlines", "today", "update", "breaking", "current events"}
        category = "general"
        if any(w in q for w in ["tech", "technology", "ai", "software", "chip", "semiconductor"]):
            category = "technology"
        elif any(w in q for w in ["finance", "market", "stocks", "stock", "economy", "fed", "bank", "invest"]):
            category = "finance"
        elif any(w in q for w in ["sports", "sport", "football", "soccer", "nba", "nfl", "mlb", "wnba", "tennis", "cricket"]):
            category = "sports"
        elif any(w in q for w in ["politics", "political", "election", "elections", "president", "congress", "senate", "house", "government", "white house", "campaign", "vote", "voting", "democrat", "republican"]):
            category = "politics"
        route = "news" if any(w in q for w in news_words) else "general"
        if category != "general" and any(w in q for w in {"latest", "news", "update", "today", "headline", "headlines"}):
            route = "news"
        return {"route": route, "category": category}

    def summarize_news(self, query: str, category: str, articles: list[dict[str, Any]], history: str = "") -> str:
        if not articles:
            return "I could not retrieve a reliable news result right now. Please retry, broaden the query, or check the API settings."
        if self.available:
            context = "\n".join(
                f"[{i+1}] {a['title']} | {a['source']} | {a.get('published_at','')} | {a.get('description','')} | {a['url']}"
                for i, a in enumerate(articles[:8])
            )
            prompt = f"""
You are NewsGenie, a careful news assistant. Answer the user's news request using ONLY the supplied article metadata.
- Lead with a concise category update.
- List 3-5 important stories.
- Attribute every story to its source and preserve uncertainty.
- Never invent facts not supported by the metadata.
- Explain that source tiers are provenance indicators, not truth guarantees.

Recent conversation:
{history[-1800:]}

Request: {query}
Category: {category}
Articles:
{context}
""".strip()
            try:
                return str(self._llm.invoke(prompt).content)
            except Exception:
                pass

        lines = [f"Latest {category} update:"]
        for i, a in enumerate(articles[:5], start=1):
            lines.append(f"{i}. {a['title']} - {a['source']} ({a.get('reliability_tier','Unrated')})")
        lines.append("Open the source links below for full context. Source tiering is a provenance aid, not a truth guarantee.")
        return "\n\n".join(lines)

    def answer_general(self, query: str, results: list[dict[str, Any]], history: str = "") -> str:
        if self.available:
            context = "\n".join(
                f"[{i+1}] {r['title']} | {r['snippet']} | {r['url']}"
                for i, r in enumerate(results[:6])
            ) or "No web search results were available."
            prompt = f"""
You are NewsGenie, a concise information assistant.
Use the retrieved web context when it is available. Distinguish established facts from uncertain or incomplete information.
If context is insufficient, say so rather than inventing details. Include source names/links from the provided context when relevant.
Use recent conversation only to resolve follow-up references.

Recent conversation:
{history[-2200:]}

Question: {query}
Retrieved web context:
{context}
""".strip()
            try:
                return str(self._llm.invoke(prompt).content)
            except Exception:
                pass

        if results:
            lines = ["I do not have an LLM API key, so here are the strongest retrieved sources for your question:"]
            for i, r in enumerate(results[:5], start=1):
                snippet = (r.get("snippet") or "").strip().replace("\n", " ")
                lines.append(f"{i}. {r['title']}\n{snippet[:350]}\n{r['url']}")
            return "\n\n".join(lines)
        return (
            "I could not retrieve web context and no LLM key is configured. "
            "Check your internet connection or add OPENAI_API_KEY/TAVILY_API_KEY in the environment."
        )
