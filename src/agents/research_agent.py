"""
Research Agent - Enhanced with Multi-Query Loop

Specialized agent for conducting iterative research on multiple topics.
Supports dynamic multi-query searches for comprehensive data collection.
"""

from strands import Agent
from src.tools import web_search, news_search
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


RESEARCH_SYSTEM_PROMPT = """You are an efficient research specialist for ESG information.

**Core Principles:**
1. EFFICIENCY FIRST - Use minimal searches to get key information
2. STRUCTURED ANSWERS - Use formatting for clarity (1-2 paragraphs with bullets)
3. AVOID REDUNDANCY - Don't repeat similar searches
4. ONE SEARCH PER TARGET - Try to get all needed info in one search per company

**Research Strategy:**
- Combine search terms when possible (e.g., "GS E&C LTIR safety performance 2023")
- Use web_search for primary research (1-2 searches per company max)
- Use news_search only if web search insufficient
- Stop searching once key information is found

**Output Format:**

### Research Findings

**[Company Name]**
[1-2 paragraphs with specific metrics and context]

**Key Metrics:**
- Metric 1: [specific data]
- Metric 2: [specific data]
- Metric 3: [specific data]

**Sources:**
- [URL 1]
- [URL 2]

If data not found after 2 searches, state: "Data not publicly available."

**Answer Style:**
- Length: 1-2 paragraphs (5-8 sentences)
- Use bullet points for metrics
- Include specific numbers and dates
- Cite sources
- Use ### for headers, ** for emphasis

Remember: Quality over quantity. One good search beats ten mediocre ones."""


def create_research_agent(
    model: str = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"
) -> Agent:
    """
    Create Research Agent with search capabilities.
    
    Args:
        model: Bedrock model ID
    
    Returns:
        Configured Research Agent
    """
    agent = Agent(
        model=model,
        tools=[web_search, news_search],
        system_prompt=RESEARCH_SYSTEM_PROMPT
    )
    
    logger.info(f"Created Research Agent with model: {model}")
    return agent


def research_multiple_companies(
    companies: List[str],
    topic: str,
    max_results_per_company: int = 5
) -> Dict[str, Any]:
    """
    Research a specific topic for multiple companies.
    
    Args:
        companies: List of company names to research
        topic: Topic to research (e.g., "LTIR", "carbon emissions")
        max_results_per_company: Max search results per company
    
    Returns:
        Dict with research results for each company
    """
    agent = create_research_agent()
    
    results = {}
    for company in companies:
        query = f"{company} {topic}"
        logger.info(f"Researching: {query}")
        
        try:
            response = agent(query)
            response_text = str(response)
            
            results[company] = {
                'query': query,
                'findings': response_text,
                'status': 'success'
            }
        except Exception as e:
            logger.error(f"Research failed for {company}: {str(e)}")
            results[company] = {
                'query': query,
                'findings': '',
                'status': 'failed',
                'error': str(e)
            }
    
    return {
        'topic': topic,
        'companies': companies,
        'results': results,
        'total_researched': len(companies),
        'successful': sum(1 for r in results.values() if r['status'] == 'success')
    }


# Create default research agent
research_agent = create_research_agent()


__all__ = [
    'research_agent',
    'create_research_agent',
    'research_multiple_companies',
    'RESEARCH_SYSTEM_PROMPT'
]
