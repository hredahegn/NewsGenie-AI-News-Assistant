from __future__ import annotations

import os
from datetime import datetime

import streamlit as st

from newsgenie.llm import LLMService
from newsgenie.news_service import NewsService
from newsgenie.web_search import WebSearchService
from newsgenie.workflow import NewsGenieWorkflow
from newsgenie.demo_data import SAMPLE_NEWS

st.set_page_config(page_title="NewsGenie", page_icon="📰", layout="wide")

st.markdown(
    """
    <style>
    .ng-card {border:1px solid rgba(120,120,120,.25);border-radius:14px;padding:14px 16px;margin:10px 0;}
    .ng-muted {opacity:.72;font-size:.9rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


def _secret(name: str, default: str = "") -> str:
    """Read a deployment secret without exposing it in the browser UI."""
    try:
        value = st.secrets.get(name, "")
        if value:
            return str(value)
    except Exception:
        pass
    return os.getenv(name, default)


def history_text(messages: list[dict], limit: int = 8) -> str:
    chunks = []
    for m in messages[-limit:]:
        chunks.append(f"{m['role'].upper()}: {m['content']}")
    return "\n".join(chunks)


@st.cache_resource
def get_workflow(openai_key: str, news_key: str, tavily_key: str, model: str):
    return NewsGenieWorkflow(
        llm=LLMService(openai_key or None, model=model),
        news=NewsService(news_key or None),
        web=WebSearchService(tavily_key or None),
    )


if "messages" not in st.session_state:
    st.session_state.messages = []

openai_key = _secret("OPENAI_API_KEY")
news_key = _secret("NEWSAPI_KEY")
tavily_key = _secret("TAVILY_API_KEY")
model = _secret("OPENAI_MODEL", "gpt-5-mini")

with st.sidebar:
    st.title("📰 NewsGenie")
    st.caption("AI-Powered Information & News Assistant")
    category = st.selectbox("News category", ["auto", "technology", "finance", "sports"], index=0)
    st.markdown("#### Service status")
    st.caption("Credentials are stored server-side and are never entered by visitors.")
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

workflow = get_workflow(openai_key, news_key, tavily_key, model)

st.title("📰 NewsGenie")
st.subheader("Reliable context, current news, and quick information in one assistant")
st.caption("Routes each request through a LangGraph workflow that distinguishes news from general information queries.")

status_cols = st.columns(3)
status_cols[0].metric("AI synthesis", "Enabled" if workflow.llm.available else "Source-first mode")
status_cols[1].metric("News", "NewsAPI + RSS" if news_key else "Google News RSS")
status_cols[2].metric("Web search", "Tavily + DDGS" if tavily_key else "DDGS")

if not workflow.llm.available:
    st.info(
        "NewsGenie is running in source-first mode. Live news and web retrieval still work; "
        "adding an OpenAI API key in Streamlit Secrets enables conversational AI synthesis."
    )

tab_chat, tab_news, tab_design = st.tabs(["💬 Assistant", "⚡ Live News", "🧭 How it works"])

with tab_chat:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ask a question or request a news update...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Routing and retrieving..."):
                result = workflow.invoke(
                    prompt,
                    selected_category=category,
                    history=history_text(st.session_state.messages[:-1]),
                )
            st.markdown(result.get("answer", "No answer was generated."))
            st.caption(
                f"Route: {result.get('route','unknown')} | Category: {result.get('category','general')} | "
                f"Retrieval: {result.get('retrieval_method','n/a')}"
            )
            if result.get("articles"):
                with st.expander("News sources"):
                    for item in result["articles"][:8]:
                        st.markdown(
                            f"- [{item['title']}]({item['url']}) - {item['source']} · "
                            f"{item.get('reliability_tier','Unrated')}"
                        )
            if result.get("search_results"):
                with st.expander("Web sources"):
                    for item in result["search_results"][:5]:
                        st.markdown(f"- [{item['title']}]({item['url']})")
            if result.get("error"):
                st.warning("A retrieval step failed, so NewsGenie used its fallback path where possible.")
        st.session_state.messages.append({"role": "assistant", "content": result.get("answer", "")})

with tab_news:
    st.markdown("### Category news")
    selected = st.radio("Choose a category", ["technology", "finance", "sports"], horizontal=True)
    topic = st.text_input("Optional topic filter", placeholder="e.g., artificial intelligence, interest rates, Premier League")
    if st.button("Refresh news", type="primary"):
        with st.spinner("Retrieving current headlines..."):
            items, method = workflow.news.fetch(selected, topic, limit=8)
        st.session_state["latest_news"] = [i.to_dict() for i in items]
        st.session_state["latest_method"] = method
        st.session_state["latest_category"] = selected

    live = st.session_state.get("latest_news", [])
    if live:
        st.caption(
            f"Retrieved via {st.session_state.get('latest_method','unknown')} "
            f"at {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        for item in live:
            st.markdown(
                f"<div class='ng-card'><b>{item['title']}</b><br>"
                f"<span class='ng-muted'>{item['source']} · {item.get('published_at','')} · "
                f"{item.get('reliability_tier','Unrated')}</span><br>"
                f"{item.get('description','')}<br><a href='{item['url']}' target='_blank'>Open source</a></div>",
                unsafe_allow_html=True,
            )
    else:
        st.info("Press Refresh news for a live retrieval. Captured project samples are shown below until then.")
        for item in SAMPLE_NEWS[selected]:
            st.markdown(
                f"<div class='ng-card'><b>{item['title']}</b><br>"
                f"<span class='ng-muted'>{item['source']} · captured {item['published_at']}</span><br>"
                f"{item['description']}<br><a href='{item['url']}' target='_blank'>Open source</a></div>",
                unsafe_allow_html=True,
            )

with tab_design:
    st.markdown("### Request workflow")
    st.code(
        """START
  ↓
Classify query + use conversation context
  ├── NEWS → NewsAPI (optional) → Google News RSS fallback → provenance checks → summarize → END
  └── GENERAL → Tavily (optional) → DDGS fallback → grounded answer → END

Streamlit Session State retains recent conversation messages across reruns.""",
        language="text",
    )
    st.markdown("### Reliability guardrails")
    st.markdown(
        "- Source links and provenance are exposed to the user.\n"
        "- Source tiers are prioritization aids, **not** automatic truth scores.\n"
        "- Retrieval failures trigger explicit fallback mechanisms.\n"
        "- AI synthesis is instructed not to invent facts beyond retrieved context.\n"
        "- Duplicate headlines are removed before display.\n"
        "- API credentials stay server-side and are not exposed to visitors."
    )
