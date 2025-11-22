"""
Unit tests for MCP servers.

Tests Bedrock Knowledge Base MCP server functionality including
retrieval, error handling, and tool integration.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from botocore.exceptions import ClientError

from mcp.bedrock_kb.tools import BedrockKBRetriever
from mcp.bedrock_kb.server import (
    BedrockKBMCPServer,
    create_mcp_server,
    get_esg_knowledge,
    search_esg_documents
)


class TestBedrockKBRetriever:
    """Test Bedrock KB Retriever class."""

    @pytest.fixture
    def retriever(self):
        """Create retriever instance with mocked boto3 client."""
        with patch('boto3.Session') as mock_session:
            mock_client = Mock()
            mock_session.return_value.client.return_value = mock_client
            retriever = BedrockKBRetriever(
                kb_id="TEST_KB_ID",
                profile_name="test_profile",
                region_name="us-west-2"
            )
            retriever.bedrock_agent_runtime = mock_client
            return retriever

    def test_initialization(self, retriever):
        """Test retriever initialization."""
        assert retriever.kb_id == "TEST_KB_ID"
        assert retriever.profile_name == "test_profile"
        assert retriever.region_name == "us-west-2"
        assert retriever.bedrock_agent_runtime is not None

    def test_retrieve_success(self, retriever):
        """Test successful retrieval."""
        mock_response = {
            'retrievalResults': [
                {
                    'content': {'text': 'Test content 1'},
                    'score': 0.95,
                    'location': {
                        'type': 'S3',
                        's3Location': {'uri': 's3://bucket/doc1.txt'}
                    },
                    'metadata': {'source': 'test'}
                },
                {
                    'content': {'text': 'Test content 2'},
                    'score': 0.85,
                    'location': {
                        'type': 'S3',
                        's3Location': {'uri': 's3://bucket/doc2.txt'}
                    },
                    'metadata': {'source': 'test'}
                }
            ]
        }

        retriever.bedrock_agent_runtime.retrieve.return_value = mock_response

        results = retriever.retrieve(query="test query", num_results=10)

        assert len(results) == 2
        assert results[0]['content'] == 'Test content 1'
        assert results[0]['score'] == 0.95
        assert results[1]['content'] == 'Test content 2'
        assert results[1]['score'] == 0.85

        retriever.bedrock_agent_runtime.retrieve.assert_called_once()

    def test_retrieve_empty_query(self, retriever):
        """Test retrieval with empty query."""
        with pytest.raises(ValueError, match="Query cannot be empty"):
            retriever.retrieve(query="", num_results=10)

    def test_retrieve_invalid_num_results(self, retriever):
        """Test retrieval with invalid num_results."""
        with pytest.raises(ValueError, match="num_results must be between"):
            retriever.retrieve(query="test", num_results=0)

        with pytest.raises(ValueError, match="num_results must be between"):
            retriever.retrieve(query="test", num_results=101)

    def test_retrieve_invalid_search_type(self, retriever):
        """Test retrieval with invalid search type."""
        with pytest.raises(ValueError, match="search_type must be one of"):
            retriever.retrieve(query="test", search_type="INVALID")

    def test_retrieve_client_error(self, retriever):
        """Test retrieval with Bedrock API error."""
        error_response = {
            'Error': {
                'Code': 'ResourceNotFoundException',
                'Message': 'Knowledge Base not found'
            }
        }
        retriever.bedrock_agent_runtime.retrieve.side_effect = ClientError(
            error_response, 'Retrieve'
        )

        with pytest.raises(ClientError):
            retriever.retrieve(query="test query")

    def test_format_results(self, retriever):
        """Test result formatting."""
        raw_results = [
            {
                'content': {'text': 'Content 1'},
                'score': 0.9,
                'location': {
                    'type': 'S3',
                    's3Location': {'uri': 's3://bucket/file.txt'}
                },
                'metadata': {'key': 'value'}
            }
        ]

        formatted = retriever._format_results(raw_results)

        assert len(formatted) == 1
        assert formatted[0]['content'] == 'Content 1'
        assert formatted[0]['score'] == 0.9
        assert formatted[0]['s3_uri'] == 's3://bucket/file.txt'
        assert formatted[0]['type'] == 'S3'


class TestMCPServerTools:
    """Test MCP server tool functions."""

    @patch('mcp.bedrock_kb.server.BedrockKBRetriever')
    def test_get_esg_knowledge_success(self, mock_retriever_class):
        """Test get_esg_knowledge tool with successful retrieval."""
        mock_retriever = Mock()
        mock_retriever.retrieve.return_value = [
            {
                'content': 'ESG content',
                'score': 0.9,
                'location': {},
                'metadata': {},
                's3_uri': 's3://bucket/doc.txt',
                'type': 'S3'
            }
        ]
        mock_retriever_class.return_value = mock_retriever

        result = get_esg_knowledge.func(query="ESG question", num_results=10)
        result_data = json.loads(result)

        assert result_data['status'] == 'success'
        assert result_data['query'] == 'ESG question'
        assert result_data['num_results'] == 1
        assert len(result_data['results']) == 1
        assert result_data['results'][0]['content'] == 'ESG content'

    @patch('mcp.bedrock_kb.server.BedrockKBRetriever')
    def test_get_esg_knowledge_no_results(self, mock_retriever_class):
        """Test get_esg_knowledge tool with no results."""
        mock_retriever = Mock()
        mock_retriever.retrieve.return_value = []
        mock_retriever_class.return_value = mock_retriever

        result = get_esg_knowledge.func(query="unknown topic", num_results=10)
        result_data = json.loads(result)

        assert result_data['status'] == 'no_results'
        assert len(result_data['results']) == 0

    @patch('mcp.bedrock_kb.server.BedrockKBRetriever')
    def test_get_esg_knowledge_error(self, mock_retriever_class):
        """Test get_esg_knowledge tool with error."""
        mock_retriever = Mock()
        mock_retriever.retrieve.side_effect = Exception("API Error")
        mock_retriever_class.return_value = mock_retriever

        result = get_esg_knowledge.func(query="test", num_results=10)
        result_data = json.loads(result)

        assert result_data['status'] == 'error'
        assert 'API Error' in result_data['message']

    @patch('mcp.bedrock_kb.server.BedrockKBRetriever')
    def test_search_esg_documents_success(self, mock_retriever_class):
        """Test search_esg_documents tool with successful search."""
        mock_retriever = Mock()
        mock_retriever.retrieve.return_value = [
            {'content': 'Doc 1', 'score': 0.9},
            {'content': 'Doc 2', 'score': 0.8}
        ]
        mock_retriever_class.return_value = mock_retriever

        result = search_esg_documents.func(
            query="search term",
            search_type="SEMANTIC",
            num_results=10
        )
        result_data = json.loads(result)

        assert result_data['status'] == 'success'
        assert result_data['search_type'] == 'SEMANTIC'
        assert result_data['num_results'] == 2

    @patch('mcp.bedrock_kb.server.BedrockKBRetriever')
    def test_search_esg_documents_invalid_param(self, mock_retriever_class):
        """Test search_esg_documents tool with invalid parameter."""
        mock_retriever = Mock()
        mock_retriever.retrieve.side_effect = ValueError("Invalid search type")
        mock_retriever_class.return_value = mock_retriever

        result = search_esg_documents.func(
            query="test",
            search_type="INVALID",
            num_results=10
        )
        result_data = json.loads(result)

        assert result_data['status'] == 'error'
        assert 'Invalid parameter' in result_data['message']


class TestBedrockKBMCPServer:
    """Test MCP Server class."""

    @patch('mcp.bedrock_kb.server.BedrockKBRetriever')
    def test_server_initialization(self, mock_retriever_class):
        """Test MCP server initialization."""
        server = BedrockKBMCPServer(kb_id="TEST_KB")

        assert server.kb_id == "TEST_KB"
        assert server.retriever is not None
        mock_retriever_class.assert_called_once_with(kb_id="TEST_KB")

    @patch('mcp.bedrock_kb.server.BedrockKBRetriever')
    def test_get_tools(self, mock_retriever_class):
        """Test get_tools method."""
        server = BedrockKBMCPServer(kb_id="TEST_KB")
        tools = server.get_tools()

        assert len(tools) == 2
        assert get_esg_knowledge in tools
        assert search_esg_documents in tools

    @patch('mcp.bedrock_kb.server.BedrockKBRetriever')
    def test_get_tool_descriptions(self, mock_retriever_class):
        """Test get_tool_descriptions method."""
        server = BedrockKBMCPServer(kb_id="TEST_KB")
        descriptions = server.get_tool_descriptions()

        assert len(descriptions) == 2
        assert descriptions[0]['name'] == 'get_esg_knowledge'
        assert descriptions[1]['name'] == 'search_esg_documents'
        assert 'description' in descriptions[0]
        assert 'description' in descriptions[1]

    @patch('mcp.bedrock_kb.server.BedrockKBRetriever')
    def test_create_mcp_server(self, mock_retriever_class):
        """Test factory function."""
        server = create_mcp_server(kb_id="FACTORY_TEST")

        assert isinstance(server, BedrockKBMCPServer)
        assert server.kb_id == "FACTORY_TEST"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
