"""
DuckDuckGo Search Tools for MCP Server
"""

import logging
from typing import List, Dict, Any
from duckduckgo_search import DDGS
from langchain.tools import tool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DuckDuckGoSearcher:
    """DuckDuckGo search wrapper."""

    def __init__(self):
        self.ddgs = DDGS()
        logger.info("DuckDuckGo searcher initialized")

    def search(self, query: str, max_results: int = 10, region: str = "kr-kr") -> List[Dict[str, Any]]:
        """Perform web search."""
        try:
            logger.info(f"Searching: {query}")
            results = list(self.ddgs.text(keywords=query, region=region, max_results=max_results))
            logger.info(f"Retrieved {len(results)} results")
            
            formatted_results = []
            for idx, result in enumerate(results, 1):
                formatted_results.append({
                    'rank': idx,
                    'title': result.get('title', ''),
                    'snippet': result.get('body', ''),
                    'url': result.get('href', ''),
                })
            return formatted_results
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            raise Exception(f"Search error: {str(e)}")

    def search_news(self, query: str, max_results: int = 10, region: str = "kr-kr") -> List[Dict[str, Any]]:
        """Search for news articles."""
        try:
            logger.info(f"Searching news: {query}")
            results = list(self.ddgs.news(keywords=query, region=region, max_results=max_results))
            logger.info(f"Retrieved {len(results)} news results")
            
            formatted_results = []
            for idx, result in enumerate(results, 1):
                formatted_results.append({
                    'rank': idx,
                    'title': result.get('title', ''),
                    'snippet': result.get('body', ''),
                    'url': result.get('url', ''),
                    'date': result.get('date', ''),
                    'source': result.get('source', '')
                })
            return formatted_results
        except Exception as e:
            logger.error(f"News search failed: {str(e)}")
            raise Exception(f"News search error: {str(e)}")


_searcher = None


def get_searcher() -> DuckDuckGoSearcher:
    """Get or create DuckDuckGo searcher instance."""
    global _searcher
    if _searcher is None:
        _searcher = DuckDuckGoSearcher()
    return _searcher


@tool
def web_search(query: str, max_results: int = 10) -> str:
    """
    Search the web using DuckDuckGo for general information.
    
    Args:
        query: Search query string
        max_results: Maximum number of results (default: 10)
    
    Returns:
        Formatted search results
    """
    try:
        searcher = get_searcher()
        results = searcher.search(query, max_results=max_results)
        
        formatted_output = f"Search results for: {query}\n\n"
        for result in results:
            formatted_output += f"[{result['rank']}] {result['title']}\n"
            formatted_output += f"URL: {result['url']}\n"
            formatted_output += f"Snippet: {result['snippet']}\n\n"
        
        return formatted_output
    except Exception as e:
        return f"Search failed: {str(e)}"


@tool
def news_search(query: str, max_results: int = 10) -> str:
    """
    Search for recent news articles using DuckDuckGo.
    
    Args:
        query: News search query
        max_results: Maximum number of results (default: 10)
    
    Returns:
        Formatted news results
    """
    try:
        searcher = get_searcher()
        results = searcher.search_news(query, max_results=max_results)
        
        formatted_output = f"News results for: {query}\n\n"
        for result in results:
            formatted_output += f"[{result['rank']}] {result['title']}\n"
            formatted_output += f"Source: {result.get('source', 'Unknown')}\n"
            formatted_output += f"Date: {result.get('date', 'N/A')}\n"
            formatted_output += f"URL: {result['url']}\n"
            formatted_output += f"Snippet: {result['snippet']}\n\n"
        
        return formatted_output
    except Exception as e:
        return f"News search failed: {str(e)}"


__all__ = ['DuckDuckGoSearcher', 'get_searcher', 'web_search', 'news_search']
