"""
DuckDuckGo Search MCP Server Package

Web search capabilities for finding external ESG information.
"""

from .server import DuckDuckGoMCPServer, get_server, get_tools
from .tools import DuckDuckGoSearcher, get_searcher, web_search, news_search

__all__ = [
    'DuckDuckGoMCPServer',
    'get_server',
    'get_tools',
    'DuckDuckGoSearcher',
    'get_searcher',
    'web_search',
    'news_search'
]
