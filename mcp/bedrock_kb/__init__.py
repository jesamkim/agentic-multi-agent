"""
Bedrock Knowledge Base MCP Server.

Provides tools for retrieving information from AWS Bedrock Knowledge Base
using hybrid search (keyword + semantic).
"""

from .server import (
    BedrockKBMCPServer,
    create_mcp_server,
    get_esg_knowledge,
    search_esg_documents
)

from .tools import (
    BedrockKBRetriever
)

__all__ = [
    'BedrockKBMCPServer',
    'create_mcp_server',
    'get_esg_knowledge',
    'search_esg_documents',
    'BedrockKBRetriever'
]

__version__ = '1.0.0'
