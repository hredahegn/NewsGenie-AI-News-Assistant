from __future__ import annotations

import os
from datetime import datetime

import streamlit as st

from newsgenie.llm import LLMService
from newsgenie.news_service import NewsService
from newsgenie.web_search import WebSearchService
from newsgenie.workflow import NewsGenieWorkflow
from newsgenie.demo_data import SAMPLE_NEWS

st.set_page_config(
    page_title="NewsGenie | Haddish Redahegn",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --ng-bg: #06111f;
        --ng-panel: rgba(12, 28, 47, 0.72);
        --ng-panel-2: rgba(14, 34, 58, 0.92);
        --ng-border: rgba(147, 197, 253, 0.16);
        --ng-text: #eef6ff;
        --ng-muted: #9fb3c8;
        --ng-cyan: #67e8f9;
        --ng-blue: #60a5fa;
        --ng-violet: #a78bfa;
        --ng-green: #5eead4;
    }

    html, body, [class*="css"] {
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 15% 5%, rgba(37, 99, 235, .22), transparent 28%),
            radial-gradient(circle at 88% 12%, rgba(124, 58, 237, .15), transparent 25%),
            radial-gradient(circle at 58% 92%, rgba(6, 182, 212, .10), transparent 30%),
            linear-gradient(145deg, #06111f 0%, #081526 44%, #07101c 100%);
        color: var(--ng-text);
    }

    [data-testid="stAppViewContainer"] > .main {
        background: transparent;
    }

    [data-testid="stHeader"] {
        background: rgba(6, 17, 31, 0.55);
        backdrop-filter: blur(14px);
        border-bottom: 1px solid rgba(148, 163, 184, 0.08);
    }

    [data-testid="stSidebar"] {
        background:
            linear-gradient(180deg, rgba(10, 25, 43, .97), rgba(8, 19, 33, .97));
        border-right: 1px solid rgba(96, 165, 250, 0.13);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.6rem;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 2.1rem;
        padding-bottom: 2rem;
    }

    .ng-sidebar-brand {
        padding: 1rem 1rem 1.1rem 1rem;
        border: 1px solid rgba(103, 232, 249, .13);
        border-radius: 18px;
        background: linear-gradient(145deg, rgba(17, 44, 72, .88), rgba(11, 27, 46, .82));
        box-shadow: 0 18px 50px rgba(0,0,0,.18);
        margin-bottom: 1.1rem;
    }

    .ng-sidebar-logo {
        font-size: 1.42rem;
        font-weight: 800;
        letter-spacing: -.03em;
        margin-bottom: .3rem;
    }

    .ng-sidebar-sub {
        color: var(--ng-muted);
        font-size: .88rem;
        line-height: 1.45;
    }

    .ng-sidebar-owner {
        display: inline-flex;
        margin-top: .85rem;
        padding: .42rem .7rem;
        border-radius: 999px;
        color: #dff8ff;
        border: 1px solid rgba(103, 232, 249, .2);
        background: rgba(14, 116, 144, .14);
        font-size: .78rem;
        font-weight: 650;
    }

    .ng-hero {
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(103, 232, 249, .16);
        border-radius: 28px;
        padding: 2.25rem 2.35rem 2.1rem 2.35rem;
        margin-bottom: 1.25rem;
        background:
            linear-gradient(125deg, rgba(15, 40, 68, .94), rgba(10, 27, 48, .90) 55%, rgba(25, 28, 63, .88));
        box-shadow: 0 28px 80px rgba(0, 0, 0, .28), inset 0 1px 0 rgba(255,255,255,.03);
    }

    .ng-hero::before {
        content: "";
        position: absolute;
        width: 420px;
        height: 420px;
        border-radius: 50%;
        right: -140px;
        top: -220px;
        background: radial-gradient(circle, rgba(96,165,250,.28), rgba(96,165,250,0) 68%);
        pointer-events: none;
    }

    .ng-hero::after {
        content: "";
        position: absolute;
        width: 330px;
        height: 330px;
        border-radius: 50%;
        left: 42%;
        bottom: -270px;
        background: radial-gradient(circle, rgba(103,232,249,.18), rgba(103,232,249,0) 70%);
        pointer-events: none;
    }

    .ng-eyebrow {
        display: inline-flex;
        align-items: center;
        gap: .45rem;
        padding: .42rem .7rem;
        border-radius: 999px;
        color: #d9f7ff;
        font-size: .74rem;
        font-weight: 750;
        letter-spacing: .08em;
        text-transform: uppercase;
        background: rgba(8, 145, 178, .13);
        border: 1px solid rgba(103,232,249,.2);
        margin-bottom: 1rem;
    }

    .ng-hero-title {
        font-size: clamp(2.35rem, 5vw, 4.4rem);
        line-height: .98;
        font-weight: 850;
        letter-spacing: -.055em;
        margin: 0;
        color: #f7fbff;
        text-shadow: 0 8px 30px rgba(0,0,0,.16);
    }

    .ng-gradient-word {
        background: linear-gradient(92deg, #f8fbff 5%, #7dd3fc 43%, #a78bfa 96%);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }

    .ng-creator {
        margin-top: .85rem;
        color: #bfd2e5;
        font-size: .95rem;
    }

    .ng-hero-copy {
        max-width: 900px;
        color: #b6c8db;
        font-size: 1.08rem;
        line-height: 1.72;
        margin-top: 1.25rem;
        margin-bottom: 0;
    }

    .ng-hero-pills {
        display: flex;
        flex-wrap: wrap;
        gap: .55rem;
        margin-top: 1.35rem;
    }

    .ng-pill {
        padding: .43rem .72rem;
        border-radius: 999px;
        background: rgba(148, 163, 184, .08);
        border: 1px solid rgba(148, 163, 184, .13);
        color: #d7e7f7;
        font-size: .77rem;
        font-weight: 650;
    }

    [data-testid="stMetric"] {
        border: 1px solid var(--ng-border);
        border-radius: 20px;
        padding: 1rem 1.05rem;
        background:
            linear-gradient(145deg, rgba(14, 34, 58, .82), rgba(10, 25, 44, .72));
        box-shadow: 0 16px 45px rgba(0,0,0,.14), inset 0 1px 0 rgba(255,255,255,.025);
        min-height: 118px;
    }

    [data-testid="stMetricLabel"] {
        color: #8fa8c0;
        font-weight: 650;
    }

    [data-testid="stMetricValue"] {
        color: #f4f9ff;
        letter-spacing: -.035em;
    }

    [data-testid="stAlert"] {
        border-radius: 18px;
        border: 1px solid rgba(96, 165, 250, .16);
        background: linear-gradient(120deg, rgba(15, 64, 104, .42), rgba(16, 42, 72, .48));
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: .42rem;
        padding: .38rem;
        border-radius: 16px;
        background: rgba(12, 29, 49, .66);
        border: 1px solid rgba(148, 163, 184, .10);
        width: fit-content;
    }

    .stTabs [data-baseweb="tab"] {
        height: 42px;
        padding: 0 .95rem;
        border-radius: 12px;
        color: #aabdd0;
        font-weight: 700;
    }

    .stTabs [aria-selected="true"] {
        color: #ecfeff !important;
        background: linear-gradient(125deg, rgba(14,116,144,.30), rgba(37,99,235,.22)) !important;
    }

    .stTabs [data-baseweb="tab-highlight"] {
        display: none;
    }

    [data-testid="stChatInput"] {
        border: 1px solid rgba(103, 232, 249, .16);
        border-radius: 18px;
        background: rgba(11, 27, 46, .84);
        box-shadow: 0 18px 60px rgba(0,0,0,.20);
    }

    [data-testid="stChatMessage"] {
        border: 1px solid rgba(148,163,184,.09);
        border-radius: 18px;
        padding: .35rem .75rem;
        background: rgba(13, 31, 52, .57);
        margin: .55rem 0;
    }

    .stButton > button {
        border-radius: 13px;
        border: 1px solid rgba(103, 232, 249, .16);
        background: linear-gradient(125deg, #0e7490, #2563eb);
        color: white;
        font-weight: 750;
        box-shadow: 0 10px 30px rgba(37, 99, 235, .18);
        transition: all .2s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        border-color: rgba(103,232,249,.38);
        box-shadow: 0 14px 36px rgba(37, 99, 235, .25);
    }

    [data-testid="stSidebar"] .stButton > button {
        background: rgba(148,163,184,.06);
        box-shadow: none;
    }

    div[data-baseweb="select"] > div,
    .stTextInput input {
        border-radius: 13px !important;
        border-color: rgba(148, 163, 184, .15) !important;
        background: rgba(7, 20, 35, .75) !important;
    }

    .ng-section-title {
        font-size: 1.7rem;
        font-weight: 800;
        letter-spacing: -.035em;
        margin: .5rem 0 1rem 0;
    }

    .ng-card {
        position: relative;
        border: 1px solid rgba(125, 211, 252, .12);
        border-radius: 20px;
        padding: 1.15rem 1.2rem 1.15rem 1.25rem;
        margin: .8rem 0;
        background:
            linear-gradient(145deg, rgba(14, 34, 58, .84), rgba(10, 25, 44, .74));
        box-shadow: 0 16px 45px rgba(0,0,0,.13);
        transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease;
    }

    .ng-card:hover {
        transform: translateY(-2px);
        border-color: rgba(103, 232, 249, .24);
        box-shadow: 0 22px 56px rgba(0,0,0,.19);
    }

    .ng-card b {
        display: inline-block;
        font-size: 1.03rem;
        line-height: 1.48;
        color: #f2f8ff;
        margin-bottom: .35rem;
    }

    .ng-muted {
        color: #8ea6bd;
        font-size: .82rem;
    }

    .ng-card a {
        display: inline-block;
        margin-top: .7rem;
        color: #75e6f7 !important;
        text-decoration: none;
        font-weight: 700;
    }

    .ng-footer {
        text-align: center;
        color: #7f96ac;
        font-size: .82rem;
        padding: 2.5rem 0 .75rem 0;
    }

    .ng-footer strong {
        color: #b8cce0;
    }

    hr {
        border-color: rgba(148,163,184,.08) !important;
    }

    @media (max-width: 768px) {
        .ng-hero {
            padding: 1.55rem 1.35rem;
            border-radius: 22px;
        }
        .ng-hero-copy {font-size: .97rem;}
        .block-container {padding-top: 1rem;}
    }
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
    st.markdown(
        """
        <div class="ng-sidebar-brand">
            <div class="ng-sidebar-logo">📰 NewsGenie</div>
            <div class="ng-sidebar-sub">AI-Powered Information & News Assistant</div>
            <div class="ng-sidebar-owner">Built by Haddish Redahegn</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    category = st.selectbox("News category", ["auto", "technology", "finance", "sports"], index=0)
    st.markdown("#### Service status")
    st.caption("Credentials stay server-side and are never entered by visitors.")
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

workflow = get_workflow(openai_key, news_key, tavily_key, model)

st.markdown(
    """
    <section class="ng-hero">
        <div class="ng-eyebrow">● Live intelligence · Multi-source retrieval</div>
        <h1 class="ng-hero-title">News<span class="ng-gradient-word">Genie</span></h1>
        <div class="ng-creator">Created by <strong>Haddish Redahegn</strong></div>
        <p class="ng-hero-copy">
            A modern AI-powered information and news assistant that separates current-news requests from general questions,
            retrieves from multiple sources, preserves context, and keeps provenance visible.
        </p>
        <div class="ng-hero-pills">
            <span class="ng-pill">LangGraph workflow</span>
            <span class="ng-pill">Live news retrieval</span>
            <span class="ng-pill">Web search fallback</span>
            <span class="ng-pill">Source transparency</span>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

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
    st.markdown("<div class='ng-section-title'>Category news</div>", unsafe_allow_html=True)
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
                f"{item.get('description','')}<br><a href='{item['url']}' target='_blank'>Open source ↗</a></div>",
                unsafe_allow_html=True,
            )
    else:
        st.info("Press Refresh news for a live retrieval. Captured project samples are shown below until then.")
        for item in SAMPLE_NEWS[selected]:
            st.markdown(
                f"<div class='ng-card'><b>{item['title']}</b><br>"
                f"<span class='ng-muted'>{item['source']} · captured {item['published_at']}</span><br>"
                f"{item['description']}<br><a href='{item['url']}' target='_blank'>Open source ↗</a></div>",
                unsafe_allow_html=True,
            )

with tab_design:
    st.markdown("<div class='ng-section-title'>Request workflow</div>", unsafe_allow_html=True)
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

st.markdown(
    "<div class='ng-footer'>NewsGenie · Designed and developed by <strong>Haddish Redahegn</strong></div>",
    unsafe_allow_html=True,
)
