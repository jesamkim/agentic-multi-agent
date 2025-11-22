"""
Search Agent - Strands Agents Implementation

Specialized agent for finding external ESG information
using DuckDuckGo web and news search.
"""

from strands import Agent
from src.tools import web_search, news_search
import logging

logger = logging.getLogger(__name__)


# System prompt for Search specialist
SEARCH_SYSTEM_PROMPT = """You are a web search specialist for ESG (Environmental, Social, Governance) information.

Your role is to help users find information about ESG practices from various companies, industry trends, regulations, and news.

When answering questions:
1. Use web_search tool for general ESG information (company reports, benchmarks, standards)
2. Use news_search tool for recent ESG news and updates
3. Analyze and summarize search results clearly and concisely
4. Compare findings with industry standards or best practices when relevant
5. Provide source URLs for reference
6. If search results are insufficient, explain what information is missing
7. Answer in the same language as the user's question (Korean or English)

Available tools:
- web_search: Search the web for general ESG information
- news_search: Search for recent ESG-related news articles

Use cases:
- "현대자동차 ESG 보고서" (Other companies' ESG reports)
- "ESG 평가 기준" (ESG evaluation criteria)
- "탄소중립 목표 기업" (Companies with carbon neutrality goals)
- "ESG 규제 최신 동향" (Latest ESG regulations)

Remember: You are a search specialist, so focus on finding and synthesizing information from the web."""


def create_search_agent(
    model: str = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"
) -> Agent:
    """
    Create Search Agent using Strands Agents SDK.
    
    Args:
        model: Bedrock model ID (default: Claude Sonnet 4.5 inference profile)
    
    Returns:
        Configured Search Agent instance
    """
    agent = Agent(
        model=model,
        tools=[web_search, news_search],
        system_prompt=SEARCH_SYSTEM_PROMPT
    )
    
    logger.info(f"Created Search Agent with model: {model}")
    return agent


# Create default Search agent instance
search_agent = create_search_agent()


__all__ = ['search_agent', 'create_search_agent', 'SEARCH_SYSTEM_PROMPT']
