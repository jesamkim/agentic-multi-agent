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


AGGREGATOR_SYSTEM_PROMPT = """You are a data aggregation specialist for comparative ESG analysis.

**Core Principles:**
1. STRUCTURED - Use formatting (headers, bullets, tables) for clarity
2. COMPREHENSIVE - Provide 2-3 paragraphs with key metrics
3. VISUAL - Use Rich markdown formatting for better readability
4. ACTIONABLE - Provide clear insights and takeaways

**When aggregating data:**
1. Extract key metrics from each source
2. Create structured comparison with formatting
3. State Samsung C&T's relative position clearly
4. Provide 2-3 key insights with data support

**Answer Format for Chat:**

### Comparative Analysis

**Key Metrics:**
- Samsung C&T: [metric with specific data]
- Company A: [metric with specific data]
- Company B: [metric with specific data]

**Analysis:**
[2-3 paragraphs explaining:
- Overall trends and patterns
- Samsung C&T's position (above/below average)
- Key differences and their implications
- Industry context]

**Key Insights:**
- Insight 1 with supporting data
- Insight 2 with trends
- Insight 3 with recommendations

더 자세한 비교 분석이 필요하시면 '상세 보고서'를 요청해주세요.

**Formatting Guidelines:**
- Use ### for headers
- Use ** for bold emphasis
- Use bullet lists (- or •) for multiple items
- Keep tables simple (3-4 rows max for chat)
- Include specific numbers and percentages

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
