# Deploy NewsGenie on Streamlit Community Cloud

## What works without paid keys

- Current category news: Google News RSS fallback
- General web retrieval: DDGS fallback
- LangGraph routing, Streamlit UI, source links, session state, and fallback behavior

Without an OpenAI API key, general questions operate in source-first mode and show retrieved web sources rather than an AI-written synthesis.

## Optional server-side secrets

In Streamlit Community Cloud, open **App settings -> Secrets** and add only the services you want:

```toml
OPENAI_API_KEY = "your-key"
OPENAI_MODEL = "gpt-5-mini"
NEWSAPI_KEY = ""
TAVILY_API_KEY = ""
```

Do not commit real API keys to GitHub.

## Deploy

1. Push this folder to a public GitHub repository.
2. Sign in to Streamlit Community Cloud with GitHub.
3. Create a new app from the repository.
4. Branch: `main`
5. Main file path: `app.py`
6. Add optional secrets in Advanced settings/App settings.
7. Deploy.

The app will receive a shareable `streamlit.app` URL.
