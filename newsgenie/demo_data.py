"""Legacy sample-data module.

The production Live News surface no longer displays static captured headlines. Keeping the
category keys here preserves compatibility with the Streamlit UI while ensuring that a failed
or empty live retrieval cannot be mistaken for current news.
"""

SAMPLE_NEWS = {
    "technology": [],
    "finance": [],
    "sports": [],
    "politics": [],
}
