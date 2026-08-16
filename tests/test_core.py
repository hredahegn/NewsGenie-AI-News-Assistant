from newsgenie.llm import LLMService
from newsgenie.reliability import reliability_tier


def test_rule_based_news_routing():
    llm = LLMService(api_key=None)
    result = llm.classify("Give me the latest technology news")
    assert result == {"route": "news", "category": "technology"}


def test_rule_based_politics_routing():
    llm = LLMService(api_key=None)
    result = llm.classify("Give me the latest politics news")
    assert result == {"route": "news", "category": "politics"}


def test_rule_based_general_routing():
    llm = LLMService(api_key=None)
    result = llm.classify("Explain what a large language model is")
    assert result["route"] == "general"


def test_source_tier():
    assert reliability_tier("https://www.reuters.com/example").startswith("Tier 1")
