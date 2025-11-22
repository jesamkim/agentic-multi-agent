"""
Aggregator Agent - Data Synthesis and Comparison

Specialized agent for collecting, analyzing, and comparing
data from multiple sources to generate comprehensive answers.
"""

from strands import Agent
from typing import List, Dict, Any
import logging
import json

logger = logging.getLogger(__name__)


AGGREGATOR_SYSTEM_PROMPT = """You are a data aggregation specialist focused on concise insights.

**Core Principles:**
1. BREVITY - Summarize in 4-6 sentences for chat
2. FOCUS - Highlight only the most important comparisons
3. ACTIONABLE - Provide clear takeaways

**When aggregating data:**
1. Extract key metrics from each source
2. Create simple comparison (3-4 companies max in summary)
3. State Samsung C&T's relative position
4. Provide 1-2 key insights

**Answer Format for Chat:**

Brief comparison:
- Samsung C&T: [key metric]
- Company A: [key metric]
- Company B: [key metric]

Key insight: [1-2 sentences]

더 자세한 비교 분석이 필요하시면 말씀해주세요.

**Important:**
- NO lengthy tables in chat responses
- NO excessive detail unless report requested
- Focus on user's specific question, not everything

Answer in user's language (Korean/English)."""


def create_aggregator_agent(
    model: str = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"
) -> Agent:
    """
    Create Aggregator Agent for data synthesis.
    
    Args:
        model: Bedrock model ID
    
    Returns:
        Configured Aggregator Agent
    """
    agent = Agent(
        model=model,
        tools=[],  # Aggregator doesn't need external tools, just processes data
        system_prompt=AGGREGATOR_SYSTEM_PROMPT
    )
    
    logger.info(f"Created Aggregator Agent with model: {model}")
    return agent


def aggregate_and_compare(
    data_sources: List[Dict[str, Any]],
    comparison_context: str
) -> str:
    """
    Aggregate data from multiple sources and generate comparative analysis.
    
    Args:
        data_sources: List of data dictionaries from various sources
        comparison_context: Context for comparison (e.g., "LTIR safety metrics")
    
    Returns:
        Comprehensive comparative analysis
    """
    agent = create_aggregator_agent()
    
    # Format data for aggregator
    data_summary = f"Comparison Context: {comparison_context}\n\n"
    data_summary += "Data Sources:\n\n"
    
    for idx, source in enumerate(data_sources, 1):
        data_summary += f"Source {idx}:\n"
        data_summary += f"{json.dumps(source, ensure_ascii=False, indent=2)}\n\n"
    
    prompt = f"""Please aggregate and compare the following data:

{data_summary}

Provide a comprehensive comparative analysis with insights."""
    
    logger.info(f"Aggregating {len(data_sources)} data sources")
    
    try:
        response = agent(prompt)
        response_text = str(response)
        return response_text
    except Exception as e:
        logger.error(f"Aggregation failed: {str(e)}")
        return f"Error during aggregation: {str(e)}"


# Create default aggregator
aggregator_agent = create_aggregator_agent()


__all__ = [
    'aggregator_agent',
    'create_aggregator_agent',
    'aggregate_and_compare',
    'AGGREGATOR_SYSTEM_PROMPT'
]
