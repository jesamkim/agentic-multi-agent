"""
Unit tests for Search Agent and DuckDuckGo MCP Server.

Tests web search capabilities for external ESG information retrieval.
"""

import pytest
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mcp.duckduckgo import (
    DuckDuckGoSearcher,
    get_searcher,
    web_search,
    news_search,
    get_tools
)
from src.agents import SearchAgent, create_search_agent


# DuckDuckGo Searcher Tests
class TestDuckDuckGoSearcher:
    """Test DuckDuckGo searcher functionality."""

    def test_searcher_initialization(self):
        """Test searcher can be initialized."""
        searcher = DuckDuckGoSearcher()
        assert searcher is not None
        assert hasattr(searcher, 'ddgs')

    def test_get_searcher_singleton(self):
        """Test get_searcher returns singleton instance."""
        searcher1 = get_searcher()
        searcher2 = get_searcher()
        assert searcher1 is searcher2

    def test_web_search_basic(self):
        """Test basic web search functionality."""
        searcher = DuckDuckGoSearcher()
        results = searcher.search(
            query="ESG reporting standards",
            max_results=3
        )

        assert isinstance(results, list)
        assert len(results) <= 3
        if results:
            assert 'rank' in results[0]
            assert 'title' in results[0]
            assert 'snippet' in results[0]
            assert 'url' in results[0]

    def test_web_search_korean(self):
        """Test web search with Korean query."""
        searcher = DuckDuckGoSearcher()
        results = searcher.search(
            query="ESG 경영",
            max_results=3,
            region="kr-kr"
        )

        assert isinstance(results, list)
        assert len(results) <= 3

    def test_news_search_basic(self):
        """Test news search functionality."""
        searcher = DuckDuckGoSearcher()
        results = searcher.search_news(
            query="ESG sustainability",
            max_results=3
        )

        assert isinstance(results, list)
        if results:
            assert 'rank' in results[0]
            assert 'title' in results[0]
            assert 'url' in results[0]

    def test_search_empty_query(self):
        """Test search with empty query."""
        searcher = DuckDuckGoSearcher()
        with pytest.raises(Exception):
            searcher.search(query="", max_results=5)


# LangChain Tool Tests
class TestDuckDuckGoTools:
    """Test LangChain tool wrappers."""

    def test_web_search_tool(self):
        """Test web_search tool."""
        result = web_search.invoke({
            "query": "carbon neutrality",
            "max_results": 3
        })

        assert isinstance(result, str)
        assert len(result) > 0
        assert "Search results for:" in result or "Search failed:" in result

    def test_news_search_tool(self):
        """Test news_search tool."""
        result = news_search.invoke({
            "query": "ESG news",
            "max_results": 3
        })

        assert isinstance(result, str)
        assert len(result) > 0
        assert "News results for:" in result or "News search failed:" in result

    def test_get_tools(self):
        """Test get_tools returns list of tools."""
        tools = get_tools()

        assert isinstance(tools, list)
        assert len(tools) == 2
        tool_names = [t.name for t in tools]
        assert 'web_search' in tool_names
        assert 'news_search' in tool_names


# Search Agent Tests
class TestSearchAgent:
    """Test Search Agent functionality."""

    @pytest.fixture
    def search_agent(self):
        """Create Search Agent instance for testing."""
        return create_search_agent()

    def test_agent_initialization(self, search_agent):
        """Test Search Agent can be initialized."""
        assert search_agent is not None
        assert search_agent.agent_name == "Search Agent"
        assert len(search_agent.tools) == 2

    def test_agent_info(self, search_agent):
        """Test getting agent information."""
        info = search_agent.get_agent_info()

        assert info['agent_name'] == "Search Agent"
        assert info['agent_type'] == "Web Search Specialist"
        assert 'capabilities' in info
        assert len(info['tool_names']) == 2

    def test_search_esg_info(self, search_agent):
        """Test searching for ESG information."""
        result = search_agent.search_esg_info(
            query="현대자동차 ESG 보고서",
            search_type="web",
            max_results=3
        )

        assert 'query' in result
        assert 'answer' in result
        assert 'search_results' in result
        assert isinstance(result['answer'], str)

    def test_search_esg_news(self, search_agent):
        """Test searching for ESG news."""
        result = search_agent.search_esg_info(
            query="삼성 ESG 최근 뉴스",
            search_type="news",
            max_results=3
        )

        assert 'query' in result
        assert 'answer' in result
        assert isinstance(result['answer'], str)

    def test_compare_companies(self, search_agent):
        """Test company comparison functionality."""
        result = search_agent.compare_companies(
            company_names=["삼성", "현대"],
            comparison_aspect="ESG practices"
        )

        assert 'companies' in result
        assert 'aspect' in result
        assert 'comparison' in result
        assert len(result['companies']) == 2

    def test_agent_invoke(self, search_agent):
        """Test direct agent invocation."""
        result = search_agent.invoke(
            user_input="Find information about ESG rating agencies"
        )

        assert 'output' in result
        assert isinstance(result['output'], str)
        assert len(result['output']) > 0


# Integration Tests
class TestSearchAgentIntegration:
    """Integration tests for Search Agent."""

    def test_agent_with_esg_query(self):
        """Test agent with real ESG query."""
        agent = create_search_agent()

        query = "What are the main ESG reporting frameworks?"
        result = agent.search_esg_info(query, max_results=5)

        assert result['query'] == query
        assert len(result['answer']) > 0
        # Should have called search tools
        assert 'intermediate_steps' in result or 'search_results' in result

    def test_agent_with_comparison(self):
        """Test agent with company comparison."""
        agent = create_search_agent()

        result = agent.compare_companies(
            company_names=["Tesla", "Toyota"],
            comparison_aspect="carbon emissions"
        )

        assert 'Tesla' in result['comparison'] or 'Toyota' in result['comparison'] or 'error' in result

    def test_agent_error_handling(self):
        """Test agent handles errors gracefully."""
        agent = create_search_agent()

        # Test with empty query
        result = agent.search_esg_info(query="", max_results=3)

        # Should not crash, should return error in result
        assert 'answer' in result
        assert isinstance(result['answer'], str)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
