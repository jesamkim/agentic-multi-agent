"""
Integration tests for ESG chatbot system.

Tests end-to-end functionality including agent initialization,
KB retrieval, and response generation.
"""

import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.esg_agent import create_esg_agent, ESGAgent


class TestESGAgentIntegration:
    """Integration tests for ESG Agent."""

    @pytest.fixture
    def mock_bedrock_response(self):
        """Mock Bedrock KB retrieval response."""
        return {
            'retrievalResults': [
                {
                    'content': {'text': 'ESG test content about sustainability'},
                    'score': 0.95,
                    'location': {
                        'type': 'S3',
                        's3Location': {'uri': 's3://bucket/doc.txt'}
                    },
                    'metadata': {}
                }
            ]
        }

    @patch('boto3.Session')
    def test_esg_agent_initialization(self, mock_session):
        """Test ESG agent can be initialized."""
        mock_client = Mock()
        mock_session.return_value.client.return_value = mock_client

        agent = create_esg_agent(kb_id="TEST_KB")

        assert agent is not None
        assert isinstance(agent, ESGAgent)
        assert agent.kb_id == "TEST_KB"
        assert len(agent.tools) > 0

    @patch('boto3.Session')
    def test_agent_response_format(self, mock_session):
        """Test that agent responses are properly formatted."""
        # This test verifies the _extract_text_from_response method works

        mock_client = Mock()
        mock_session.return_value.client.return_value = mock_client

        agent = create_esg_agent(kb_id="TEST_KB")

        # Test with string response
        text = agent._extract_text_from_response("Simple text")
        assert text == "Simple text"

        # Test with list response (Claude format)
        list_response = [
            {'type': 'text', 'text': 'First part'},
            {'type': 'text', 'text': 'Second part'}
        ]
        text = agent._extract_text_from_response(list_response)
        assert 'First part' in text
        assert 'Second part' in text

        # Test with dict response
        dict_response = {'text': 'Dict content'}
        text = agent._extract_text_from_response(dict_response)
        assert text == 'Dict content'

    @patch('boto3.Session')
    def test_agent_info(self, mock_session):
        """Test agent info retrieval."""
        mock_client = Mock()
        mock_session.return_value.client.return_value = mock_client

        agent = create_esg_agent(kb_id="TEST_KB")
        info = agent.get_agent_info()

        assert 'agent_name' in info
        assert 'agent_type' in info
        assert info['agent_type'] == 'ESG Specialist'
        assert 'capabilities' in info
        assert len(info['capabilities']) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
