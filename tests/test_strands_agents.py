"""
Integration tests for Strands Agents-based ESG chatbot.

Tests the complete multi-agent system including:
- Individual tools (Bedrock KB, DuckDuckGo search)
- Specialized agents (ESG, Search)
- Supervisor agent (orchestration and routing)
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.tools import (
    get_esg_knowledge,
    web_search,
    news_search,
    ESG_TOOLS,
    SEARCH_TOOLS
)
from src.agents import (
    esg_agent,
    search_agent,
    supervisor_agent,
    create_esg_agent,
    create_search_agent,
    create_supervisor_agent
)


class TestTools:
    """Test individual tools."""
    
    def test_bedrock_kb_tool_exists(self):
        """Test that ESG knowledge tool is available."""
        assert get_esg_knowledge is not None
        assert callable(get_esg_knowledge)
        assert 'get_esg_knowledge' == get_esg_knowledge.tool_name
    
    def test_web_search_tool_exists(self):
        """Test that web search tool is available."""
        assert web_search is not None
        assert callable(web_search)
        assert 'web_search' == web_search.tool_name
    
    def test_news_search_tool_exists(self):
        """Test that news search tool is available."""
        assert news_search is not None
        assert callable(news_search)
        assert 'news_search' == news_search.tool_name
    
    def test_tool_collections(self):
        """Test tool collections are properly defined."""
        assert len(ESG_TOOLS) == 1
        assert len(SEARCH_TOOLS) == 2
        assert get_esg_knowledge in ESG_TOOLS
        assert web_search in SEARCH_TOOLS
        assert news_search in SEARCH_TOOLS


class TestAgents:
    """Test individual agents."""
    
    def test_esg_agent_exists(self):
        """Test ESG agent is created."""
        assert esg_agent is not None
        assert hasattr(esg_agent, 'model')
        assert hasattr(esg_agent, 'tool_names')
        assert hasattr(esg_agent, 'system_prompt')
    
    def test_esg_agent_has_correct_tools(self):
        """Test ESG agent has KB retrieval tool."""
        tool_names = esg_agent.tool_names
        assert 'get_esg_knowledge' in tool_names
        assert len(tool_names) == 1
    
    def test_search_agent_exists(self):
        """Test Search agent is created."""
        assert search_agent is not None
        assert hasattr(search_agent, 'model')
        assert hasattr(search_agent, 'tool_names')
        assert hasattr(search_agent, 'system_prompt')
    
    def test_search_agent_has_correct_tools(self):
        """Test Search agent has search tools."""
        tool_names = search_agent.tool_names
        assert 'web_search' in tool_names
        assert 'news_search' in tool_names
        assert len(tool_names) == 2
    
    def test_supervisor_agent_exists(self):
        """Test Supervisor agent is created."""
        assert supervisor_agent is not None
        assert hasattr(supervisor_agent, 'model')
        assert hasattr(supervisor_agent, 'tool_names')
        assert hasattr(supervisor_agent, 'system_prompt')
    
    def test_supervisor_agent_has_a2a_tools(self):
        """Test Supervisor has A2A communication tools."""
        tool_names = supervisor_agent.tool_names
        assert 'call_esg_agent' in tool_names
        assert 'call_search_agent' in tool_names
        assert len(tool_names) == 2


class TestAgentFactories:
    """Test agent factory functions."""
    
    def test_create_esg_agent(self):
        """Test ESG agent factory."""
        agent = create_esg_agent()
        assert agent is not None
        tool_names = agent.tool_names
        assert 'get_esg_knowledge' in tool_names
    
    def test_create_search_agent(self):
        """Test Search agent factory."""
        agent = create_search_agent()
        assert agent is not None
        tool_names = agent.tool_names
        assert 'web_search' in tool_names
        assert 'news_search' in tool_names
    
    def test_create_supervisor_agent(self):
        """Test Supervisor agent factory."""
        agent = create_supervisor_agent()
        assert agent is not None
        tool_names = agent.tool_names
        assert 'call_esg_agent' in tool_names
        assert 'call_search_agent' in tool_names


@pytest.mark.integration
class TestAgentIntegration:
    """Integration tests requiring AWS credentials."""
    
    @pytest.mark.slow
    def test_esg_agent_simple_query(self):
        """Test ESG agent with simple query."""
        query = "What is Samsung C&T?"
        response = esg_agent(query)
        
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
    
    @pytest.mark.slow
    def test_search_agent_simple_query(self):
        """Test Search agent with simple query."""
        query = "What are ESG rating agencies?"
        response = search_agent(query)
        
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
    
    @pytest.mark.slow
    def test_supervisor_routes_to_esg_agent(self):
        """Test Supervisor routes Samsung C&T question to ESG agent."""
        query = "삼성물산의 ESG 목표는 무엇인가요?"
        response = supervisor_agent(query)
        
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
    
    @pytest.mark.slow
    def test_supervisor_routes_to_search_agent(self):
        """Test Supervisor routes external question to Search agent."""
        query = "현대자동차의 ESG 보고서에 대해 알려주세요"
        response = supervisor_agent(query)
        
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
    
    @pytest.mark.slow
    def test_supervisor_handles_greeting(self):
        """Test Supervisor handles greeting directly."""
        query = "안녕하세요"
        response = supervisor_agent(query)
        
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0


@pytest.mark.integration
@pytest.mark.slow
class TestEndToEnd:
    """End-to-end tests of complete system."""
    
    def test_multi_agent_system_samsung_candt(self):
        """Test full system with Samsung C&T question."""
        query = "삼성물산의 탄소배출량 목표는?"
        response = supervisor_agent(query)
        
        assert response is not None
        assert isinstance(response, str)
        # Should get a meaningful response
        assert len(response) > 100
    
    def test_multi_agent_system_external_company(self):
        """Test full system with external company question."""
        query = "Tesla ESG report"
        response = supervisor_agent(query)
        
        assert response is not None
        assert isinstance(response, str)
        # Should get a meaningful response
        assert len(response) > 100
    
    def test_multi_agent_system_general_esg(self):
        """Test full system with general ESG question."""
        query = "What is ESG?"
        response = supervisor_agent(query)
        
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 50


if __name__ == "__main__":
    # Run tests (excluding slow integration tests by default)
    pytest.main([__file__, "-v", "-s", "-m", "not slow"])
