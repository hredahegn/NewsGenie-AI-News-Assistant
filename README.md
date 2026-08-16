# Haddish Signal — AI-Powered News & Information Assistant

Haddish Signal is a Streamlit + LangGraph application created by Haddish Redahegn. It distinguishes general information questions from current-news requests, retrieves external information, preserves conversation context, and exposes its sources.

## Live-use architecture

- **News requests:** NewsAPI when configured, with Google News RSS fallback
- **General information:** Tavily when configured, with DDGS fallback
- **AI synthesis:** OpenAI when configured; otherwise source-first deterministic output
- **Workflow:** LangGraph
- **UI/session:** Streamlit
- **Live categories:** Technology, Finance, Sports, and Politics

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy

See `DEPLOYMENT.md`. API keys are read only from server-side Streamlit Secrets or environment variables; visitors never enter or see them.

## Important limitation

Haddish Signal reduces misinformation risk through transparent sourcing, recency, deduplication, fallback handling, and provenance indicators. It does not claim to automatically determine whether every report is true.
