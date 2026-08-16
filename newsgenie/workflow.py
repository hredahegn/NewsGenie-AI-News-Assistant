from __future__ import annotations

from typing import TypedDict, Literal

from langgraph.graph import StateGraph, START, END

from .llm import LLMService
from .news_service import NewsService
from .web_search import WebSearchService


class NewsGenieState(TypedDict, total=False):
    query: str
    selected_category: str
    history: str
    route: Literal["news", "general"]
    category: str
    articles: list[dict]
    search_results: list[dict]
    retrieval_method: str
    answer: str
    error: str


class NewsGenieWorkflow:
    def __init__(
        self,
        llm: LLMService | None = None,
        news: NewsService | None = None,
        web: WebSearchService | None = None,
    ):
        self.llm = llm or LLMService()
        self.news = news or NewsService()
        self.web = web or WebSearchService()
        self.graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(NewsGenieState)
        builder.add_node("classify", self._classify)
        builder.add_node("fetch_news", self._fetch_news)
        builder.add_node("compose_news", self._compose_news)
        builder.add_node("web_search", self._web_search)
        builder.add_node("compose_general", self._compose_general)

        builder.add_edge(START, "classify")
        builder.add_conditional_edges(
            "classify",
            lambda state: state.get("route", "general"),
            {"news": "fetch_news", "general": "web_search"},
        )
        builder.add_edge("fetch_news", "compose_news")
        builder.add_edge("compose_news", END)
        builder.add_edge("web_search", "compose_general")
        builder.add_edge("compose_general", END)
        return builder.compile()

    def _classify(self, state: NewsGenieState) -> NewsGenieState:
        decision = self.llm.classify(
            state.get("query", ""),
            history=state.get("history", ""),
            selected_category=state.get("selected_category", "auto"),
        )
        return {"route": decision["route"], "category": decision["category"]}

    def _fetch_news(self, state: NewsGenieState) -> NewsGenieState:
        try:
            articles, method = self.news.fetch(
                state.get("category", "general"),
                query=state.get("query", ""),
                limit=8,
            )
            return {"articles": [a.to_dict() for a in articles], "retrieval_method": method}
        except Exception as exc:
            return {"articles": [], "retrieval_method": "failed", "error": str(exc)}

    def _compose_news(self, state: NewsGenieState) -> NewsGenieState:
        answer = self.llm.summarize_news(
            state.get("query", ""),
            state.get("category", "general"),
            state.get("articles", []),
            state.get("history", ""),
        )
        return {"answer": answer}

    def _web_search(self, state: NewsGenieState) -> NewsGenieState:
        try:
            results, method = self.web.search(state.get("query", ""), limit=5)
            return {"search_results": [r.to_dict() for r in results], "retrieval_method": method}
        except Exception as exc:
            return {"search_results": [], "retrieval_method": "failed", "error": str(exc)}

    def _compose_general(self, state: NewsGenieState) -> NewsGenieState:
        answer = self.llm.answer_general(
            state.get("query", ""),
            state.get("search_results", []),
            state.get("history", ""),
        )
        return {"answer": answer}

    def invoke(self, query: str, selected_category: str = "auto", history: str = "") -> NewsGenieState:
        return self.graph.invoke(
            {"query": query, "selected_category": selected_category, "history": history}
        )
