"""
Strands Agents - Multi-Agent ESG Chatbot System

Provides specialized agents for ESG information:
- ESG Agent: Samsung C&T knowledge base specialist
- Search Agent: External ESG information specialist
- Supervisor Agent: Orchestrator for routing queries
"""

from .esg_agent import esg_agent, create_esg_agent, ESG_SYSTEM_PROMPT
from .search_agent import search_agent, create_search_agent, SEARCH_SYSTEM_PROMPT
from .supervisor_agent import (
    supervisor_agent,
    create_supervisor_agent,
    call_esg_agent,
    call_search_agent,
    SUPERVISOR_SYSTEM_PROMPT
)

__all__ = [
    # Agent instances
    'esg_agent',
    'search_agent',
    'supervisor_agent',
    # Factory functions
    'create_esg_agent',
    'create_search_agent',
    'create_supervisor_agent',
    # A2A tools
    'call_esg_agent',
    'call_search_agent',
    # System prompts
    'ESG_SYSTEM_PROMPT',
    'SEARCH_SYSTEM_PROMPT',
    'SUPERVISOR_SYSTEM_PROMPT'
]
