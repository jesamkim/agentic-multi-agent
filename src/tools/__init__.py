"""
Strands Agent Tools

Collection of tools for ESG chatbot agents:
- Bedrock Knowledge Base retrieval
- Web search (DuckDuckGo)
- News search (DuckDuckGo)
- Report generation (HTML/PDF)
"""

from .bedrock_kb_tool import get_esg_knowledge, BedrockKBRetriever, get_retriever
from .search_tools import web_search, news_search, DuckDuckGoSearcher, get_searcher
from .report_tools import generate_detailed_report, create_html_report

# ESG Knowledge Base tools
ESG_TOOLS = [get_esg_knowledge]

# Web Search tools
SEARCH_TOOLS = [web_search, news_search]

# Report generation tools
REPORT_TOOLS = [generate_detailed_report]

# All tools combined
ALL_TOOLS = ESG_TOOLS + SEARCH_TOOLS + REPORT_TOOLS

__all__ = [
    # Tools
    'get_esg_knowledge',
    'web_search',
    'news_search',
    'generate_detailed_report',
    # Tool collections
    'ESG_TOOLS',
    'SEARCH_TOOLS',
    'REPORT_TOOLS',
    'ALL_TOOLS',
    # Classes
    'BedrockKBRetriever',
    'DuckDuckGoSearcher',
    'get_retriever',
    'get_searcher',
    # Functions
    'create_html_report'
]
