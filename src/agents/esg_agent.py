"""
ESG Agent - Strands Agents Implementation

Specialized agent for answering ESG questions about Samsung C&T
using Bedrock Knowledge Base retrieval.
"""

from strands import Agent
from src.tools import get_esg_knowledge
import logging

logger = logging.getLogger(__name__)


# System prompt for ESG specialist
ESG_SYSTEM_PROMPT = """You are an ESG specialist for Samsung C&T.

**Core Principles:**
1. CONCISE FIRST - Answer in 3-5 sentences unless detailed report requested
2. EFFICIENT RETRIEVAL - Use get_esg_knowledge tool once, with precise query
3. CITE KEY DATA - Mention specific numbers/metrics only when relevant

**When answering:**
1. Call get_esg_knowledge ONCE with a well-crafted query
2. Extract key information from retrieved documents
3. Provide focused summary with 1-2 key metrics
4. If user needs more detail, suggest: "상세 보고서가 필요하시면 말씀해주세요"

**Answer Style:**
- SHORT: 3-5 sentences for chat responses
- FOCUSED: Highlight most relevant data point
- ACTIONABLE: Direct answer to user's question
- BILINGUAL: Match user's language (Korean/English)

**Example Good Answer:**
"삼성물산의 2024년 탄소배출량은 543만 톤CO2e이며, 2030년까지 30% 감축을 목표로 합니다. 재생에너지 전환과 에너지 효율화를 통해 달성할 예정입니다."

Knowledge Base: Samsung C&T 2025 Sustainability Report (124 pages)

Remember: Brief and helpful > comprehensive but exhausting."""


def create_esg_agent(
    model: str = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"
) -> Agent:
    """
    Create ESG Agent using Strands Agents SDK.
    
    Args:
        model: Bedrock model ID (default: Claude Sonnet 4.5 inference profile)
    
    Returns:
        Configured ESG Agent instance
    """
    agent = Agent(
        model=model,
        tools=[get_esg_knowledge],
        system_prompt=ESG_SYSTEM_PROMPT
    )
    
    logger.info(f"Created ESG Agent with model: {model}")
    return agent


# Create default ESG agent instance
esg_agent = create_esg_agent()


__all__ = ['esg_agent', 'create_esg_agent', 'ESG_SYSTEM_PROMPT']
