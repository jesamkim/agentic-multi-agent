"""
DuckDuckGo Search Tools for Strands Agents

Provides web and news search capabilities for finding
external ESG information and industry benchmarks.
"""

import logging
from typing import List, Dict, Any
from duckduckgo_search import DDGS
from strands import tool

logger = logging.getLogger(__name__)


class DuckDuckGoSearcher:
    """DuckDuckGo search wrapper for web and news search."""
    
    def __init__(self):
        """Initialize DuckDuckGo searcher."""
        self.ddgs = DDGS()
        logger.info("DuckDuckGo searcher initialized")
    
    def search_web(
        self,
        query: str,
        max_results: int = 10,
        region: str = "kr-kr"
    ) -> List[Dict[str, Any]]:
        """
        Perform web search.
        
        Args:
            query: Search query
            max_results: Maximum results to return
            region: Region code (default: kr-kr for Korea)
            
        Returns:
            List of search results
        """
        try:
            logger.info(f"Web search: {query}")
            results = list(self.ddgs.text(
                keywords=query,
                region=region,
                max_results=max_results
            ))
            logger.info(f"Found {len(results)} web results")
            
            formatted = []
            for idx, result in enumerate(results, 1):
                formatted.append({
                    'rank': idx,
                    'title': result.get('title', ''),
                    'snippet': result.get('body', ''),
                    'url': result.get('href', '')
                })
            return formatted
            
        except Exception as e:
            logger.error(f"Web search failed: {str(e)}")
            raise
    
    def search_news(
        self,
        query: str,
        max_results: int = 10,
        region: str = "kr-kr"
    ) -> List[Dict[str, Any]]:
        """
        Search for news articles.
        
        Args:
            query: News search query
            max_results: Maximum results to return
            region: Region code
            
        Returns:
            List of news results
        """
        try:
            logger.info(f"News search: {query}")
            results = list(self.ddgs.news(
                keywords=query,
                region=region,
                max_results=max_results
            ))
            logger.info(f"Found {len(results)} news results")
            
            formatted = []
            for idx, result in enumerate(results, 1):
                formatted.append({
                    'rank': idx,
                    'title': result.get('title', ''),
                    'snippet': result.get('body', ''),
                    'url': result.get('url', ''),
                    'date': result.get('date', ''),
                    'source': result.get('source', '')
                })
            return formatted
            
        except Exception as e:
            logger.error(f"News search failed: {str(e)}")
            raise


# Global searcher instance
_searcher = None


def get_searcher() -> DuckDuckGoSearcher:
    """Get or create searcher instance."""
    global _searcher
    if _searcher is None:
        _searcher = DuckDuckGoSearcher()
    return _searcher


@tool
def web_search(query: str, max_results: int = 10) -> str:
    """
    Search the web for general ESG information and industry data.
    
    Use this tool to find information about:
    - Other companies' ESG reports and practices
    - Industry benchmarks and standards
    - ESG regulations and frameworks
    - Sustainability trends and best practices
    
    Args:
        query: Search query (e.g., "현대자동차 ESG 보고서 2025")
        max_results: Number of results to retrieve (default: 10)
    
    Returns:
        Formatted web search results with titles, snippets, and URLs
    """
    try:
        searcher = get_searcher()
        results = searcher.search_web(query, max_results)
        
        if not results:
            return f"No web results found for: {query}"
        
        formatted = f"Web Search Results for: {query}\n\n"
        for result in results:
            formatted += f"[{result['rank']}] {result['title']}\n"
            formatted += f"URL: {result['url']}\n"
            formatted += f"{result['snippet']}\n\n"
        
        return formatted
        
    except Exception as e:
        return f"Web search error: {str(e)}"


@tool
def news_search(query: str, max_results: int = 10) -> str:
    """
    Search for recent news articles about ESG topics.
    
    Use this tool to find:
    - Recent ESG-related news and announcements
    - Company sustainability updates
    - Industry developments and trends
    - Regulatory changes and compliance news
    
    Args:
        query: News search query (e.g., "삼성물산 ESG 최근 뉴스")
        max_results: Number of results to retrieve (default: 10)
    
    Returns:
        Formatted news results with titles, dates, sources, and URLs
    """
    try:
        searcher = get_searcher()
        results = searcher.search_news(query, max_results)
        
        if not results:
            return f"No news results found for: {query}"
        
        formatted = f"News Search Results for: {query}\n\n"
        for result in results:
            formatted += f"[{result['rank']}] {result['title']}\n"
            formatted += f"Source: {result.get('source', 'Unknown')} | Date: {result.get('date', 'N/A')}\n"
            formatted += f"URL: {result['url']}\n"
            formatted += f"{result['snippet']}\n\n"
        
        return formatted
        
    except Exception as e:
        return f"News search error: {str(e)}"


__all__ = ['DuckDuckGoSearcher', 'get_searcher', 'web_search', 'news_search']
