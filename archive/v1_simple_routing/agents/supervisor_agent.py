"""
Supervisor Agent - Strands Agents Implementation

Orchestrator agent that routes questions to specialized agents.
Implements Agent-to-Agent (A2A) communication pattern.
"""

from strands import Agent, tool
from .esg_agent import esg_agent
from .search_agent import search_agent
import logging

logger = logging.getLogger(__name__)


# System prompt for Supervisor (orchestrator)
SUPERVISOR_SYSTEM_PROMPT = """You are a supervisor agent for an ESG chatbot system.

Your role is to analyze user questions and route them to the appropriate specialist agent:

1. call_esg_agent - For questions about Samsung C&T's ESG practices
   - Use for: Samsung C&T sustainability report questions
   - Topics: Samsung C&T's environmental initiatives, social responsibility, governance
   - Examples: "삼성물산의 탄소배출량은?", "Samsung C&T's ESG goals"

2. call_search_agent - For questions about other companies or general ESG topics
   - Use for: Other companies' ESG practices, industry benchmarks, regulations
   - Topics: Competitors, industry trends, ESG standards, news
   - Examples: "현대자동차 ESG 보고서", "ESG rating agencies"

3. Direct response - For general greetings, clarifications, or simple questions
   - Use for: Greetings, thank yous, clarification requests
   - Examples: "안녕하세요", "Thank you", "What can you help me with?"

Decision-making guidelines:
- If the question mentions "Samsung C&T" or "삼성물산" → call_esg_agent
- If the question asks about other companies → call_search_agent
- If the question is about ESG concepts/standards/news → call_search_agent
- If unclear which agent to use, ask clarifying questions first
- You can call both agents if the question requires information from both sources

Always be professional, helpful, and answer in the same language as the user's question."""


# Wrap specialized agents as tools for A2A communication
@tool
def call_esg_agent(query: str) -> str:
    """
    Call the ESG specialist agent to answer questions about Samsung C&T.
    
    Use this tool when the user asks about:
    - Samsung C&T's sustainability report
    - Samsung C&T's ESG practices and initiatives
    - Samsung C&T's environmental, social, or governance data
    
    Args:
        query: User question about Samsung C&T's ESG
    
    Returns:
        Answer from the ESG specialist agent
    """
    logger.info(f"Routing to ESG Agent: {query[:100]}...")
    try:
        response = esg_agent(query)
        return response
    except Exception as e:
        return f"Error calling ESG agent: {str(e)}"


@tool
def call_search_agent(query: str) -> str:
    """
    Call the search specialist agent to find external ESG information.
    
    Use this tool when the user asks about:
    - Other companies' ESG reports or practices
    - Industry benchmarks and comparisons
    - ESG regulations, standards, and frameworks
    - Recent ESG news and trends
    
    Args:
        query: User question about external ESG information
    
    Returns:
        Answer from the search specialist agent
    """
    logger.info(f"Routing to Search Agent: {query[:100]}...")
    try:
        response = search_agent(query)
        return response
    except Exception as e:
        return f"Error calling search agent: {str(e)}"


def create_supervisor_agent(
    model: str = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"
) -> Agent:
    """
    Create Supervisor Agent using Strands Agents SDK.
    
    The supervisor orchestrates other agents using A2A communication pattern.
    
    Args:
        model: Bedrock model ID (default: Claude Sonnet 4.5 inference profile)
    
    Returns:
        Configured Supervisor Agent instance
    """
    agent = Agent(
        model=model,
        tools=[call_esg_agent, call_search_agent],
        system_prompt=SUPERVISOR_SYSTEM_PROMPT
    )
    
    logger.info(f"Created Supervisor Agent with model: {model}")
    return agent


# Create default Supervisor agent instance
supervisor_agent = create_supervisor_agent()


__all__ = [
    'supervisor_agent',
    'create_supervisor_agent',
    'call_esg_agent',
    'call_search_agent',
    'SUPERVISOR_SYSTEM_PROMPT'
]
