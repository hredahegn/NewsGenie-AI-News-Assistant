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
    :root{
      --bg0:#020712;
      --bg1:#06101f;
      --panel:rgba(8,20,37,.72);
      --panel2:rgba(13,31,53,.88);
      --line:rgba(117,226,247,.18);
      --cyan:#63e7f6;
      --blue:#5aa7ff;
      --violet:#9b8cff;
      --red:#ff5a6b;
      --text:#f5f9ff;
      --muted:#a8bbcf;
      --green:#55e6b7;
    }

    html,body,[class*="css"]{
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .stApp{
      color:var(--text);
      background:
        linear-gradient(rgba(12,28,46,.18) 1px, transparent 1px),
        linear-gradient(90deg, rgba(12,28,46,.18) 1px, transparent 1px),
        radial-gradient(circle at 12% 0%, rgba(20,109,255,.22), transparent 26%),
        radial-gradient(circle at 92% 5%, rgba(132,63,255,.16), transparent 25%),
        radial-gradient(circle at 60% 100%, rgba(0,207,230,.10), transparent 28%),
        linear-gradient(145deg,#020712 0%,#06101f 48%,#040a15 100%);
      background-size: 48px 48px,48px 48px,auto,auto,auto,auto;
    }

    [data-testid="stHeader"]{
      background:rgba(2,7,18,.45);
      backdrop-filter:blur(18px);
      border-bottom:1px solid rgba(255,255,255,.04);
    }

    [data-testid="stSidebar"]{
      background:
        linear-gradient(180deg,rgba(7,18,33,.98),rgba(3,10,20,.98));
      border-right:1px solid rgba(99,231,246,.12);
    }

    .block-container{
      max-width:1500px;
      padding-top:1.7rem;
      padding-bottom:2rem;
    }

    .ng-sidebar-brand{
      position:relative;
      overflow:hidden;
      padding:1rem;
      border-radius:20px;
      border:1px solid rgba(99,231,246,.14);
      background:linear-gradient(145deg,rgba(15,40,68,.9),rgba(8,22,40,.86));
      box-shadow:0 18px 60px rgba(0,0,0,.22);
      margin-bottom:1.1rem;
    }
    .ng-sidebar-brand:after{
      content:"";
      position:absolute;
      width:120px;height:120px;border-radius:50%;
      right:-35px;top:-55px;
      background:radial-gradient(circle,rgba(90,167,255,.30),transparent 68%);
    }
    .ng-sidebar-logo{font-size:1.45rem;font-weight:900;letter-spacing:-.04em;}
    .ng-sidebar-sub{font-size:.84rem;color:var(--muted);line-height:1.5;margin-top:.25rem;}
    .ng-sidebar-owner{
      display:inline-flex;margin-top:.8rem;padding:.38rem .65rem;border-radius:999px;
      border:1px solid rgba(99,231,246,.18);background:rgba(8,145,178,.12);
      color:#dffaff;font-size:.76rem;font-weight:750;
    }

    .ng-cinema{
      position:relative;
      overflow:hidden;
      border:1px solid rgba(99,231,246,.18);
      border-radius:30px;
      min-height:430px;
      margin-bottom:1.25rem;
      background:
        linear-gradient(90deg,rgba(2,7,18,.18),rgba(2,7,18,.08)),
        radial-gradient(circle at 72% 45%,rgba(0,190,255,.12),transparent 28%),
        linear-gradient(125deg,rgba(7,24,43,.96),rgba(3,13,26,.95) 54%,rgba(11,18,43,.96));
      box-shadow:0 34px 100px rgba(0,0,0,.38), inset 0 1px 0 rgba(255,255,255,.03);
    }
    .ng-cinema:before{
      content:"";
      position:absolute;inset:0;
      background:
        linear-gradient(rgba(64,131,185,.08) 1px,transparent 1px),
        linear-gradient(90deg,rgba(64,131,185,.08) 1px,transparent 1px);
      background-size:38px 38px;
      mask-image:linear-gradient(90deg,transparent,black 28%,black 100%);
      pointer-events:none;
    }
    .ng-cinema:after{
      content:"";
      position:absolute;
      left:0;right:0;top:-30%;
      height:26%;
      background:linear-gradient(180deg,transparent,rgba(99,231,246,.10),transparent);
      filter:blur(1px);
      animation:scan 7s linear infinite;
      pointer-events:none;
    }
    @keyframes scan{0%{transform:translateY(0)}100%{transform:translateY(560px)}}

    .ng-cinema-inner{
      position:relative;z-index:2;
      display:grid;grid-template-columns:1.05fr .95fr;gap:1.2rem;
      align-items:center;min-height:430px;padding:2.4rem 2.5rem;
    }
    .ng-kicker{
      display:inline-flex;align-items:center;gap:.5rem;
      padding:.42rem .72rem;border-radius:999px;
      border:1px solid rgba(99,231,246,.20);
      background:rgba(10,114,144,.13);
      color:#dcfbff;font-size:.74rem;font-weight:850;letter-spacing:.09em;text-transform:uppercase;
      margin-bottom:1rem;
    }
    .ng-kicker-dot{width:7px;height:7px;border-radius:50%;background:var(--green);box-shadow:0 0 18px var(--green);}
    .ng-title{
      margin:0;color:white;font-weight:950;letter-spacing:-.055em;
      line-height:.94;font-size:clamp(2.8rem,5.7vw,5.3rem);
      text-shadow:0 14px 40px rgba(0,0,0,.32);
    }
    .ng-title span{
      background:linear-gradient(92deg,#ffffff 0%,#7de9fa 48%,#9e8cff 100%);
      -webkit-background-clip:text;background-clip:text;color:transparent;
    }
    .ng-owner{margin-top:.85rem;color:#c6d6e7;font-size:.95rem;}
    .ng-owner b{color:#fff;}
    .ng-copy{max-width:700px;margin-top:1.25rem;color:#afc2d6;line-height:1.7;font-size:1.04rem;}
    .ng-pills{display:flex;flex-wrap:wrap;gap:.5rem;margin-top:1.3rem;}
    .ng-pill{
      padding:.42rem .7rem;border-radius:999px;
      background:rgba(150,170,190,.07);border:1px solid rgba(150,170,190,.12);
      color:#d9e8f7;font-size:.76rem;font-weight:700;
    }

    .ng-stage{position:relative;height:330px;}
    .ng-orbit{
      position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);
      width:250px;height:250px;border-radius:50%;
      border:1px solid rgba(99,231,246,.18);
      box-shadow:0 0 80px rgba(0,190,255,.08), inset 0 0 70px rgba(90,167,255,.07);
      animation:orbitpulse 4s ease-in-out infinite;
    }
    .ng-orbit:before,.ng-orbit:after{
      content:"";position:absolute;border-radius:50%;inset:22px;
      border:1px dashed rgba(155,140,255,.20);
      animation:spin 18s linear infinite;
    }
    .ng-orbit:after{inset:48px;border-color:rgba(99,231,246,.20);animation-direction:reverse;animation-duration:12s;}
    @keyframes spin{to{transform:rotate(360deg)}}
    @keyframes orbitpulse{50%{box-shadow:0 0 120px rgba(0,190,255,.14),inset 0 0 90px rgba(90,167,255,.10)}}

    .ng-core{
      position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);
      width:145px;height:145px;border-radius:50%;
      background:
        radial-gradient(circle at 34% 32%,#d9fbff 0 4%,transparent 5%),
        radial-gradient(circle at 65% 28%,#7df5ff 0 3%,transparent 4%),
        radial-gradient(circle at 40% 65%,#8ea3ff 0 3%,transparent 4%),
        radial-gradient(circle at 67% 68%,#69e9ff 0 3%,transparent 4%),
        conic-gradient(from 30deg,#2457ff,#00c3df,#9b6dff,#1d8fff,#2457ff);
      box-shadow:0 0 40px rgba(0,199,255,.38),0 0 110px rgba(77,82,255,.20);
      filter:saturate(1.15);
    }
    .ng-core:before{
      content:"AI";position:absolute;inset:22px;border-radius:50%;
      display:flex;align-items:center;justify-content:center;
      background:rgba(1,8,20,.76);border:1px solid rgba(255,255,255,.15);
      color:#eaffff;font-size:2rem;font-weight:950;letter-spacing:-.08em;
      box-shadow:inset 0 0 30px rgba(99,231,246,.10);
    }

    .ng-beam{position:absolute;height:1px;background:linear-gradient(90deg,transparent,#4ce9ff,transparent);transform-origin:left center;opacity:.65;}
    .beam1{width:150px;left:27%;top:36%;transform:rotate(-22deg)}
    .beam2{width:165px;left:56%;top:46%;transform:rotate(22deg)}
    .beam3{width:145px;left:29%;top:68%;transform:rotate(18deg)}
    .beam4{width:150px;left:55%;top:66%;transform:rotate(-20deg)}

    .ng-float{
      position:absolute;width:150px;padding:.75rem .8rem;
      border-radius:15px;border:1px solid rgba(99,231,246,.15);
      background:linear-gradient(145deg,rgba(10,30,52,.88),rgba(7,19,35,.88));
      box-shadow:0 16px 46px rgba(0,0,0,.28);
      backdrop-filter:blur(12px);
    }
    .ng-float .tag{font-size:.64rem;letter-spacing:.09em;text-transform:uppercase;color:#80edfb;font-weight:850;}
    .ng-float .value{font-size:.9rem;color:#f4fbff;font-weight:800;margin-top:.2rem;}
    .ng-float .tiny{font-size:.68rem;color:#8da4bb;margin-top:.2rem;line-height:1.35;}
    .f1{left:0;top:28px}.f2{right:0;top:42px}.f3{left:6px;bottom:25px}.f4{right:0;bottom:18px}
    .f2{border-color:rgba(255,90,107,.18)} .f2 .tag{color:#ff7d8b}
    .f4{border-color:rgba(85,230,183,.18)} .f4 .tag{color:#68edc5}

    .ng-statusbar{
      display:grid;grid-template-columns:repeat(3,1fr);gap:.8rem;margin:.25rem 0 1rem;
    }
    .ng-status{
      border:1px solid rgba(99,231,246,.12);border-radius:18px;
      background:linear-gradient(145deg,rgba(9,25,44,.80),rgba(5,16,30,.72));
      padding:1rem 1.05rem;box-shadow:0 14px 44px rgba(0,0,0,.14);
    }
    .ng-status-label{font-size:.72rem;color:#86a0b8;text-transform:uppercase;letter-spacing:.08em;font-weight:800;}
    .ng-status-value{margin-top:.28rem;font-size:1.2rem;color:#f4fbff;font-weight:900;letter-spacing:-.025em;}
    .ng-status-value em{font-style:normal;color:var(--cyan);}
    .ng-status-sub{margin-top:.25rem;color:#7e94aa;font-size:.72rem;}

    [data-testid="stAlert"]{
      border-radius:18px;border:1px solid rgba(90,167,255,.14);
      background:linear-gradient(120deg,rgba(15,62,101,.40),rgba(13,39,68,.44));
    }

    .stTabs [data-baseweb="tab-list"]{
      gap:.35rem;padding:.35rem;border-radius:15px;
      background:rgba(8,22,39,.68);border:1px solid rgba(255,255,255,.07);width:fit-content;
    }
    .stTabs [data-baseweb="tab"]{
      height:42px;padding:0 .95rem;border-radius:11px;color:#aebfd0;font-weight:760;
    }
    .stTabs [aria-selected="true"]{
      color:#f3feff!important;background:linear-gradient(125deg,rgba(10,116,144,.32),rgba(37,99,235,.22))!important;
    }
    .stTabs [data-baseweb="tab-highlight"]{display:none}

    [data-testid="stChatInput"]{
      border:1px solid rgba(99,231,246,.18);border-radius:18px;
      background:rgba(6,18,33,.88);box-shadow:0 18px 60px rgba(0,0,0,.22);
    }
    [data-testid="stChatMessage"]{
      border:1px solid rgba(255,255,255,.07);border-radius:18px;
      background:linear-gradient(145deg,rgba(11,27,47,.64),rgba(8,21,37,.58));
      padding:.35rem .75rem;margin:.55rem 0;
    }
    .stButton>button{
      border-radius:13px;border:1px solid rgba(99,231,246,.16);
      background:linear-gradient(125deg,#087c9a,#2455d8);color:white;font-weight:800;
      box-shadow:0 12px 34px rgba(36,85,216,.20);transition:all .2s ease;
    }
    .stButton>button:hover{transform:translateY(-1px);box-shadow:0 16px 42px rgba(36,85,216,.28);}
    [data-testid="stSidebar"] .stButton>button{background:rgba(255,255,255,.04);box-shadow:none;}
    div[data-baseweb="select"]>div,.stTextInput input{
      border-radius:13px!important;border-color:rgba(255,255,255,.10)!important;background:rgba(3,13,25,.74)!important;
    }

    .ng-section-title{font-size:1.65rem;font-weight:900;letter-spacing:-.035em;margin:.45rem 0 .95rem;}
    .ng-card{
      border:1px solid rgba(99,231,246,.12);border-radius:20px;padding:1.12rem 1.18rem;margin:.78rem 0;
      background:linear-gradient(145deg,rgba(11,29,50,.84),rgba(7,20,36,.78));
      box-shadow:0 16px 48px rgba(0,0,0,.15);transition:.18s ease;
    }
    .ng-card:hover{transform:translateY(-2px);border-color:rgba(99,231,246,.26);box-shadow:0 24px 58px rgba(0,0,0,.21);}
    .ng-card b{display:inline-block;color:#f4faff;font-size:1.02rem;line-height:1.45;margin-bottom:.3rem;}
    .ng-muted{color:#8da4bb;font-size:.8rem;}
    .ng-card a{display:inline-block;margin-top:.65rem;color:#70e7f6!important;font-weight:800;text-decoration:none;}
    .ng-footer{text-align:center;color:#758ba1;font-size:.8rem;padding:2.4rem 0 .5rem;}
    .ng-footer strong{color:#b8cadb;}

    @media(max-width:900px){
      .ng-cinema-inner{grid-template-columns:1fr;padding:1.6rem;min-height:auto}
      .ng-stage{height:300px;margin-top:.5rem}
      .ng-statusbar{grid-template-columns:1fr}
      .ng-title{font-size:3rem}
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def _secret(name: str, default: str = "") -> str:
    try:
        value = st.secrets.get(name, "")
        if value:
            return str(value)
    except Exception:
        pass
    return os.getenv(name, default)


def history_text(messages: list[dict], limit: int = 8) -> str:
    return "\n".join(f"{m['role'].upper()}: {m['content']}" for m in messages[-limit:])


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
          <div class="ng-sidebar-sub">AI-powered information, live-news retrieval, and source-aware answers.</div>
          <div class="ng-sidebar-owner">Built by Haddish Redahegn</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    category = st.selectbox("News category", ["auto", "technology", "finance", "sports"], index=0)
    st.markdown("#### Service status")
    st.caption("Credentials remain server-side and are never entered by visitors.")
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

workflow = get_workflow(openai_key, news_key, tavily_key, model)

ai_value = "AI synthesis" if workflow.llm.available else "Source-first"
ai_sub = "OpenAI enabled" if workflow.llm.available else "Grounded retrieval mode"
news_value = "NewsAPI + RSS" if news_key else "Google News RSS"
news_sub = "Live headline retrieval"
web_value = "Tavily + DDGS" if tavily_key else "DDGS"
web_sub = "General web retrieval"

st.html(
    f"""
    <section class="ng-cinema">
      <div class="ng-cinema-inner">
        <div>
          <div class="ng-kicker"><span class="ng-kicker-dot"></span> LIVE INTELLIGENCE WORKSPACE</div>
          <h1 class="ng-title">News<span>Genie</span></h1>
          <div class="ng-owner">Created by <b>Haddish Redahegn</b></div>
          <div class="ng-copy">
            Navigate the news cycle with an AI-assisted verification workflow that separates
            live-news requests from general questions, retrieves external evidence, exposes
            sources, and keeps the conversation grounded in what was actually found.
          </div>
          <div class="ng-pills">
            <div class="ng-pill">⚡ Real-time headlines</div>
            <div class="ng-pill">🧭 Query routing</div>
            <div class="ng-pill">🔗 Source provenance</div>
            <div class="ng-pill">🧠 LangGraph workflow</div>
          </div>
        </div>
        <div class="ng-stage">
          <div class="ng-beam beam1"></div><div class="ng-beam beam2"></div>
          <div class="ng-beam beam3"></div><div class="ng-beam beam4"></div>
          <div class="ng-orbit"></div><div class="ng-core"></div>

          <div class="ng-float f1">
            <div class="tag">SOURCE CHECK</div>
            <div class="value">Provenance exposed</div>
            <div class="tiny">Every retrieved item keeps a visible source link.</div>
          </div>
          <div class="ng-float f2">
            <div class="tag">RISK SIGNAL</div>
            <div class="value">Verify before trust</div>
            <div class="tiny">Source tiers guide review; they do not claim absolute truth.</div>
          </div>
          <div class="ng-float f3">
            <div class="tag">LIVE SIGNAL</div>
            <div class="value">{news_value}</div>
            <div class="tiny">Current category and topic retrieval.</div>
          </div>
          <div class="ng-float f4">
            <div class="tag">AI ROUTER</div>
            <div class="value">News ↔ General</div>
            <div class="tiny">LangGraph directs each query to the right retrieval path.</div>
          </div>
        </div>
      </div>
    </section>

    <div class="ng-statusbar">
      <div class="ng-status">
        <div class="ng-status-label">AI synthesis</div>
        <div class="ng-status-value"><em>{ai_value}</em></div>
        <div class="ng-status-sub">{ai_sub}</div>
      </div>
      <div class="ng-status">
        <div class="ng-status-label">News engine</div>
        <div class="ng-status-value">{news_value}</div>
        <div class="ng-status-sub">{news_sub}</div>
      </div>
      <div class="ng-status">
        <div class="ng-status-label">Web search</div>
        <div class="ng-status-value">{web_value}</div>
        <div class="ng-status-sub">{web_sub}</div>
      </div>
    </div>
    """
)

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
    st.markdown("<div class='ng-section-title'>Live category intelligence</div>", unsafe_allow_html=True)
    selected = st.radio("Choose a category", ["technology", "finance", "sports"], horizontal=True)
    topic = st.text_input(
        "Optional topic filter",
        placeholder="e.g., artificial intelligence, interest rates, Premier League",
    )
    if st.button("Refresh live news", type="primary"):
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
        st.info("Press Refresh live news for a current retrieval. Captured project samples are shown below until then.")
        for item in SAMPLE_NEWS[selected]:
            st.markdown(
                f"<div class='ng-card'><b>{item['title']}</b><br>"
                f"<span class='ng-muted'>{item['source']} · captured {item['published_at']}</span><br>"
                f"{item['description']}<br><a href='{item['url']}' target='_blank'>Open source ↗</a></div>",
                unsafe_allow_html=True,
            )

with tab_design:
    st.markdown("<div class='ng-section-title'>Intelligence workflow</div>", unsafe_allow_html=True)
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
