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
    page_title="Haddish Signal | AI News Intelligence",
    page_icon="assets/haddish_signal_icon.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
:root{
  --bg0:#f8fbff;
  --bg1:#eef7fb;
  --panel:rgba(255,255,255,.78);
  --panel2:rgba(255,255,255,.92);
  --line:rgba(44,122,170,.15);
  --cyan:#00aeca;
  --blue:#2f73f2;
  --violet:#7658e8;
  --red:#df5b68;
  --text:#12243a;
  --muted:#60738a;
  --green:#16a97b;
}

html,body,[class*="css"]{
  font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
}

.stApp{
  color:var(--text);
  background:
    linear-gradient(rgba(35,99,145,.035) 1px,transparent 1px),
    linear-gradient(90deg,rgba(35,99,145,.035) 1px,transparent 1px),
    radial-gradient(circle at 12% 2%,rgba(92,207,234,.30),transparent 30%),
    radial-gradient(circle at 88% 7%,rgba(166,139,255,.22),transparent 28%),
    radial-gradient(circle at 68% 92%,rgba(255,190,133,.20),transparent 28%),
    linear-gradient(145deg,#fbfdff 0%,#eef8fc 46%,#ffffff 100%);
  background-size:44px 44px,44px 44px,auto,auto,auto,auto;
}

[data-testid="stHeader"]{
  background:rgba(255,255,255,.72);
  backdrop-filter:blur(20px) saturate(1.2);
  border-bottom:1px solid rgba(22,75,120,.07);
}

[data-testid="stSidebar"]{
  background:linear-gradient(180deg,rgba(255,255,255,.96),rgba(242,249,252,.96));
  border-right:1px solid rgba(43,113,160,.12);
  box-shadow:12px 0 35px rgba(36,79,116,.06);
}

.block-container{max-width:1500px;padding-top:1.55rem;padding-bottom:2rem;}

.ng-sidebar-brand{
  position:relative;overflow:hidden;padding:1rem;border-radius:22px;
  border:1px solid rgba(52,133,180,.14);
  background:linear-gradient(145deg,rgba(255,255,255,.98),rgba(230,247,252,.92));
  box-shadow:0 18px 45px rgba(40,104,145,.14),inset 0 1px 0 rgba(255,255,255,.95);
  margin-bottom:1.1rem;
}
.ng-sidebar-brand:after{
  content:"";position:absolute;width:150px;height:150px;border-radius:50%;right:-42px;top:-70px;
  background:radial-gradient(circle,rgba(72,190,222,.32),transparent 67%);
}
.ng-sidebar-logo{font-size:1.45rem;font-weight:950;letter-spacing:-.04em;color:#10263e;}
.ng-sidebar-sub{font-size:.84rem;color:#667b91;line-height:1.5;margin-top:.25rem;}
.ng-sidebar-owner{
  display:inline-flex;margin-top:.8rem;padding:.4rem .7rem;border-radius:999px;
  border:1px solid rgba(0,174,202,.18);background:rgba(0,174,202,.08);
  color:#0d6171;font-size:.76rem;font-weight:800;
}

.ng-cinema{
  position:relative;overflow:hidden;border:1px solid rgba(57,126,171,.15);border-radius:32px;
  min-height:440px;margin-bottom:1.25rem;
  background:
    radial-gradient(circle at 76% 42%,rgba(65,202,229,.34),transparent 24%),
    radial-gradient(circle at 62% 18%,rgba(118,96,232,.16),transparent 25%),
    radial-gradient(circle at 92% 78%,rgba(255,183,113,.16),transparent 28%),
    linear-gradient(128deg,rgba(255,255,255,.98),rgba(240,251,255,.95) 52%,rgba(249,246,255,.96));
  box-shadow:0 34px 90px rgba(52,104,143,.17),0 10px 25px rgba(52,104,143,.08),inset 0 1px 0 rgba(255,255,255,1);
  transform-style:preserve-3d;
}
.ng-cinema:before{
  content:"";position:absolute;inset:0;
  background:
    linear-gradient(rgba(45,116,163,.055) 1px,transparent 1px),
    linear-gradient(90deg,rgba(45,116,163,.055) 1px,transparent 1px);
  background-size:36px 36px;mask-image:linear-gradient(90deg,transparent 0%,rgba(0,0,0,.55) 38%,black 100%);
  pointer-events:none;
}
.ng-cinema:after{
  content:"";position:absolute;width:430px;height:430px;border-radius:50%;right:-120px;top:-160px;
  background:radial-gradient(circle,rgba(255,255,255,.96) 0%,rgba(122,225,243,.35) 30%,rgba(122,225,243,0) 70%);
  filter:blur(2px);pointer-events:none;
}

.ng-cinema-inner{
  position:relative;z-index:2;display:grid;grid-template-columns:1.02fr .98fr;gap:1.3rem;
  align-items:center;min-height:440px;padding:2.45rem 2.55rem;perspective:1000px;
}
.ng-kicker{
  display:inline-flex;align-items:center;gap:.5rem;padding:.43rem .75rem;border-radius:999px;
  border:1px solid rgba(0,174,202,.18);background:rgba(255,255,255,.74);
  color:#0a6d80;font-size:.74rem;font-weight:900;letter-spacing:.09em;text-transform:uppercase;
  box-shadow:0 8px 24px rgba(45,122,160,.08);margin-bottom:1rem;
}
.ng-kicker-dot{width:7px;height:7px;border-radius:50%;background:var(--green);box-shadow:0 0 16px rgba(22,169,123,.45);}
.ng-title{
  margin:0;color:#13283f;font-weight:950;letter-spacing:-.055em;line-height:.94;
  font-size:clamp(2.8rem,5.7vw,5.3rem);text-shadow:0 10px 30px rgba(77,121,153,.12);
}
.ng-title span{
  background:linear-gradient(92deg,#178ca5 0%,#2f73f2 52%,#7658e8 100%);
  -webkit-background-clip:text;background-clip:text;color:transparent;
}
.ng-owner{margin-top:.85rem;color:#66798d;font-size:.95rem;}.ng-owner b{color:#1a334d;}
.ng-copy{max-width:700px;margin-top:1.25rem;color:#526a82;line-height:1.7;font-size:1.04rem;}
.ng-pills{display:flex;flex-wrap:wrap;gap:.5rem;margin-top:1.3rem;}
.ng-pill{
  padding:.43rem .72rem;border-radius:999px;background:rgba(255,255,255,.82);
  border:1px solid rgba(63,128,169,.12);color:#35536f;font-size:.76rem;font-weight:760;
  box-shadow:0 8px 22px rgba(48,107,145,.08);
}

.ng-stage{position:relative;height:340px;perspective:900px;transform-style:preserve-3d;}
.ng-orbit{
  position:absolute;left:50%;top:50%;width:270px;height:270px;border-radius:50%;
  transform:translate(-50%,-50%) rotateX(60deg) rotateZ(-10deg);
  border:2px solid rgba(0,174,202,.22);
  box-shadow:0 38px 55px rgba(34,102,145,.16),0 0 80px rgba(45,115,242,.12),inset 0 0 55px rgba(255,255,255,.95);
  background:radial-gradient(circle,rgba(255,255,255,.78),rgba(201,244,250,.22) 48%,rgba(255,255,255,0) 72%);
  animation:floatorb 5.5s ease-in-out infinite;
}
.ng-orbit:before,.ng-orbit:after{
  content:"";position:absolute;border-radius:50%;inset:22px;border:2px dashed rgba(118,88,232,.22);
  animation:spin 17s linear infinite;
}
.ng-orbit:after{inset:52px;border-color:rgba(0,174,202,.25);animation-direction:reverse;animation-duration:11s;}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes floatorb{50%{transform:translate(-50%,-53%) rotateX(60deg) rotateZ(-7deg)}}

.ng-core{
  position:absolute;left:50%;top:50%;width:155px;height:155px;border-radius:50%;
  transform:translate(-50%,-50%) translateZ(45px);
  background:
    radial-gradient(circle at 30% 24%,rgba(255,255,255,1) 0 9%,rgba(255,255,255,.2) 10%,transparent 25%),
    radial-gradient(circle at 34% 30%,#bff7ff 0 10%,transparent 35%),
    radial-gradient(circle at 68% 66%,rgba(118,88,232,.85),transparent 42%),
    radial-gradient(circle at 62% 32%,rgba(47,115,242,.88),transparent 44%),
    linear-gradient(145deg,#50d9e9,#77bdf6 48%,#9c8cf3);
  box-shadow:0 22px 35px rgba(48,97,139,.22),0 0 45px rgba(0,174,202,.28),0 0 100px rgba(118,88,232,.14),inset -18px -20px 30px rgba(62,76,140,.18),inset 14px 12px 28px rgba(255,255,255,.65);
  filter:saturate(1.05);
}
.ng-core:before{
  content:"AI";position:absolute;inset:25px;border-radius:50%;display:flex;align-items:center;justify-content:center;
  background:rgba(255,255,255,.72);border:1px solid rgba(255,255,255,.95);
  color:#24527a;font-size:2rem;font-weight:950;letter-spacing:-.08em;
  box-shadow:inset 0 0 28px rgba(85,203,222,.20),0 8px 20px rgba(45,89,124,.10);
  backdrop-filter:blur(8px);
}

.ng-beam{position:absolute;height:2px;background:linear-gradient(90deg,transparent,rgba(0,174,202,.72),rgba(47,115,242,.55),transparent);transform-origin:left center;opacity:.8;filter:drop-shadow(0 2px 3px rgba(0,174,202,.18));}
.beam1{width:155px;left:27%;top:36%;transform:rotate(-22deg)}
.beam2{width:170px;left:56%;top:46%;transform:rotate(22deg)}
.beam3{width:150px;left:29%;top:68%;transform:rotate(18deg)}
.beam4{width:155px;left:55%;top:66%;transform:rotate(-20deg)}

.ng-float{
  position:absolute;width:158px;padding:.78rem .84rem;border-radius:16px;
  border:1px solid rgba(62,126,166,.15);
  background:linear-gradient(145deg,rgba(255,255,255,.92),rgba(236,249,253,.82));
  box-shadow:0 18px 36px rgba(46,99,137,.17),0 4px 10px rgba(46,99,137,.07),inset 0 1px 0 rgba(255,255,255,1);
  backdrop-filter:blur(14px);transform-style:preserve-3d;transition:.22s ease;
}
.ng-float:hover{transform:translateY(-4px) scale(1.02)!important;box-shadow:0 26px 44px rgba(46,99,137,.20);}
.ng-float .tag{font-size:.64rem;letter-spacing:.09em;text-transform:uppercase;color:#07839b;font-weight:900;}
.ng-float .value{font-size:.9rem;color:#17334d;font-weight:850;margin-top:.2rem;}
.ng-float .tiny{font-size:.68rem;color:#6d8093;margin-top:.2rem;line-height:1.35;}
.f1{left:0;top:24px;transform:rotateY(7deg) rotateX(2deg)}
.f2{right:0;top:38px;transform:rotateY(-8deg) rotateX(2deg);border-color:rgba(223,91,104,.18)}
.f3{left:8px;bottom:24px;transform:rotateY(6deg) rotateX(-2deg)}
.f4{right:0;bottom:18px;transform:rotateY(-7deg) rotateX(-2deg);border-color:rgba(22,169,123,.18)}
.f2 .tag{color:#c94f5c}.f4 .tag{color:#128a67}

.ng-statusbar{display:grid;grid-template-columns:repeat(3,1fr);gap:.8rem;margin:.25rem 0 1rem;}
.ng-status{
  border:1px solid rgba(50,124,170,.12);border-radius:20px;
  background:linear-gradient(145deg,rgba(255,255,255,.94),rgba(239,248,252,.88));
  padding:1rem 1.05rem;box-shadow:0 16px 36px rgba(47,99,136,.10),inset 0 1px 0 rgba(255,255,255,1);
}
.ng-status-label{font-size:.72rem;color:#71869a;text-transform:uppercase;letter-spacing:.08em;font-weight:850;}
.ng-status-value{margin-top:.28rem;font-size:1.2rem;color:#19344e;font-weight:900;letter-spacing:-.025em;}
.ng-status-value em{font-style:normal;color:#06849c}.ng-status-sub{margin-top:.25rem;color:#7a8da0;font-size:.72rem;}

[data-testid="stAlert"]{
  border-radius:18px;border:1px solid rgba(47,115,242,.12)!important;
  background:linear-gradient(120deg,rgba(232,246,255,.95),rgba(245,249,255,.95))!important;
  color:#24425e!important;box-shadow:0 10px 28px rgba(50,108,148,.07);
}

.stTabs [data-baseweb="tab-list"]{
  gap:.35rem;padding:.35rem;border-radius:16px;background:rgba(255,255,255,.86);
  border:1px solid rgba(55,122,164,.10);box-shadow:0 10px 26px rgba(46,102,138,.07);width:fit-content;
}
.stTabs [data-baseweb="tab"]{height:42px;padding:0 .95rem;border-radius:11px;color:#587087;font-weight:780;}
.stTabs [aria-selected="true"]{color:#15324c!important;background:linear-gradient(125deg,rgba(183,240,249,.75),rgba(215,226,255,.80))!important;}
.stTabs [data-baseweb="tab-highlight"]{display:none}

[data-testid="stChatInput"]{
  border:1px solid rgba(57,128,169,.14);border-radius:18px;background:rgba(255,255,255,.94);
  box-shadow:0 18px 44px rgba(47,101,137,.10);
}
[data-testid="stChatMessage"]{
  border:1px solid rgba(54,125,167,.09);border-radius:18px;
  background:linear-gradient(145deg,rgba(255,255,255,.92),rgba(243,250,253,.88));
  padding:.35rem .75rem;margin:.55rem 0;box-shadow:0 10px 28px rgba(47,101,137,.06);
}

.stButton>button{
  border-radius:13px;border:1px solid rgba(47,115,242,.12);
  background:linear-gradient(125deg,#20b5cf,#3f78f0);color:white;font-weight:850;
  box-shadow:0 12px 28px rgba(47,115,242,.18);transition:all .2s ease;
}
.stButton>button:hover{transform:translateY(-2px);box-shadow:0 18px 34px rgba(47,115,242,.23);}
[data-testid="stSidebar"] .stButton>button{background:rgba(255,255,255,.85);color:#29465e;box-shadow:0 8px 22px rgba(47,101,137,.07);}

div[data-baseweb="select"]>div,.stTextInput input{
  border-radius:13px!important;border-color:rgba(53,122,163,.12)!important;background:rgba(255,255,255,.92)!important;
  color:#1d3852!important;
}

.ng-section-title{font-size:1.65rem;font-weight:900;letter-spacing:-.035em;margin:.45rem 0 .95rem;color:#17334d;}
.ng-card{
  border:1px solid rgba(54,126,168,.11);border-radius:20px;padding:1.12rem 1.18rem;margin:.78rem 0;
  background:linear-gradient(145deg,rgba(255,255,255,.96),rgba(241,249,252,.90));
  box-shadow:0 16px 38px rgba(48,100,136,.10),inset 0 1px 0 rgba(255,255,255,1);transition:.18s ease;
}
.ng-card:hover{transform:translateY(-3px);border-color:rgba(0,174,202,.20);box-shadow:0 24px 44px rgba(48,100,136,.14);}
.ng-card b{display:inline-block;color:#18354f;font-size:1.02rem;line-height:1.45;margin-bottom:.3rem;}
.ng-muted{color:#708499;font-size:.8rem;}
.ng-card a{display:inline-block;margin-top:.65rem;color:#087f97!important;font-weight:850;text-decoration:none;}
.ng-footer{text-align:center;color:#7b8ea1;font-size:.8rem;padding:2.4rem 0 .5rem;}.ng-footer strong{color:#3b536b;}

@media(max-width:900px){
  .ng-cinema-inner{grid-template-columns:1fr;padding:1.45rem;min-height:auto;gap:1rem}
  .ng-stage{
    height:auto;margin-top:.75rem;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));
    gap:.8rem;perspective:none;transform-style:flat;
  }
  .ng-orbit,.ng-core,.ng-beam{display:none}
  .ng-float,.f1,.f2,.f3,.f4{
    position:relative;left:auto;right:auto;top:auto;bottom:auto;width:auto;min-width:0;
    transform:none!important;padding:.9rem 1rem;border-radius:18px;
  }
  .ng-float:hover{transform:translateY(-2px)!important}
  .ng-statusbar{grid-template-columns:1fr}.ng-title{font-size:3rem}
}
@media(max-width:600px){
  .ng-cinema{border-radius:24px;min-height:auto}
  .ng-cinema-inner{padding:1.1rem}
  .ng-stage{grid-template-columns:1fr;gap:.7rem}
  .ng-title{font-size:2.65rem}
  .ng-copy{font-size:.96rem;line-height:1.6}
  .ng-pills{gap:.4rem}
  .ng-pill{font-size:.72rem;padding:.4rem .62rem}
  .ng-float .value{font-size:1rem}
  .ng-float .tiny{font-size:.75rem;line-height:1.45}
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
          <div class="ng-sidebar-logo">◉ Haddish Signal</div>
          <div class="ng-sidebar-sub">AI-powered information, live-news retrieval, and source-aware answers.</div>
          <div class="ng-sidebar-owner">Built by Haddish Redahegn</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    category = st.selectbox("News category", ["auto", "technology", "finance", "sports", "politics"], index=0)
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
          <h1 class="ng-title">Haddish<span> Signal</span></h1>
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
        "Haddish Signal is running in source-first mode. Live news and web retrieval still work; "
        "adding an OpenAI API key in Streamlit Secrets enables conversational AI synthesis."
    )

tab_chat, tab_news, tab_design = st.tabs(
    ["💬 Assistant", "⚡ Live News", "🧭 How it works"],
    default="⚡ Live News",
)

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
                st.warning("A retrieval step failed, so Haddish Signal used its fallback path where possible.")
        st.session_state.messages.append({"role": "assistant", "content": result.get("answer", "")})

with tab_news:
    st.markdown("<div class='ng-section-title'>Live category intelligence</div>", unsafe_allow_html=True)
    selected = st.radio(
        "Choose a category",
        ["technology", "finance", "sports", "politics"],
        index=3,
        horizontal=True,
    )
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
        samples = SAMPLE_NEWS.get(selected, [])
        if not samples:
            st.caption("Politics is configured for live retrieval. Click Refresh live news to fetch current headlines.")
        for item in samples:
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
    "<div class='ng-footer'>Haddish Signal · Designed and developed by <strong>Haddish Redahegn</strong></div>",
    unsafe_allow_html=True,
)