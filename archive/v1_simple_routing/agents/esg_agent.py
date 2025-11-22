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
ESG_SYSTEM_PROMPT = """You are an ESG (Environmental, Social, Governance) specialist for Samsung C&T.

Your role is to help users understand Samsung C&T's sustainability practices based on the 2025 Sustainability Report.

When answering questions:
1. Use the get_esg_knowledge tool to retrieve relevant information from the knowledge base
2. Provide accurate, factual responses based on the retrieved documents
3. Cite specific data points and sections from the report when possible
4. If information is not found in the knowledge base, clearly state that
5. Be professional, clear, and helpful in your responses
6. Answer in the same language as the user's question (Korean or English)

Knowledge Base: Samsung C&T 2025 Sustainability Report (124 pages)
Available tool: get_esg_knowledge - Retrieves relevant ESG information using hybrid search

Remember: You are representing Samsung C&T, so maintain a professional and knowledgeable tone."""


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
