"""
MCP Server implementation for Bedrock Knowledge Base tools.

This module provides LangChain tool wrappers for Bedrock KB retrieval functions,
allowing agents to use these tools in their workflows.
"""

from langchain.tools import tool
from typing import List, Dict
import json
import logging

from .tools import BedrockKBRetriever

logger = logging.getLogger(__name__)


@tool
def get_esg_knowledge(query: str, num_results: int = 10) -> str:
    """
    Retrieve ESG knowledge from Bedrock Knowledge Base.

    Use this tool when users ask about ESG topics, sustainability practices,
    environmental impact, social responsibility, or governance matters related
    to Samsung C&T 2025 Sustainability Report.

    Args:
        query: User query or question about ESG topics
        num_results: Number of results to return (default: 10)

    Returns:
        JSON string containing retrieved documents with content and metadata
    """
    try:
        retriever = BedrockKBRetriever()
        results = retriever.retrieve(query=query, num_results=num_results)

        if not results:
            return json.dumps({
                "status": "no_results",
                "message": "No relevant information found in the knowledge base.",
                "results": []
            })

        return json.dumps({
            "status": "success",
            "query": query,
            "num_results": len(results),
            "results": results
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error in get_esg_knowledge: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": str(e),
            "results": []
        })


@tool
def search_esg_documents(
    query: str,
    search_type: str = "HYBRID",
    num_results: int = 10
) -> str:
    """
    Search ESG documents with configurable search type.

    Supports different search strategies:
    - HYBRID: Combines keyword and semantic search (recommended)
    - SEMANTIC: Pure semantic/vector search
    - KEYWORD: Pure keyword/text matching

    Args:
        query: Search query
        search_type: Search type - "HYBRID", "SEMANTIC", or "KEYWORD"
        num_results: Number of results to return (default: 10)

    Returns:
        JSON string containing search results with content and metadata
    """
    try:
        retriever = BedrockKBRetriever()
        results = retriever.retrieve(
            query=query,
            num_results=num_results,
            search_type=search_type.upper()
        )

        if not results:
            return json.dumps({
                "status": "no_results",
                "message": "No relevant documents found.",
                "search_type": search_type,
                "results": []
            })

        return json.dumps({
            "status": "success",
            "query": query,
            "search_type": search_type,
            "num_results": len(results),
            "results": results
        }, ensure_ascii=False, indent=2)

    except ValueError as e:
        logger.error(f"Invalid parameter in search_esg_documents: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": f"Invalid parameter: {str(e)}",
            "results": []
        })
    except Exception as e:
        logger.error(f"Error in search_esg_documents: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": str(e),
            "results": []
        })


class BedrockKBMCPServer:
    """
    MCP Server for Bedrock Knowledge Base tools.

    Provides a centralized interface for managing and accessing
    Bedrock KB retrieval tools.
    """

    def __init__(self, kb_id: str = "HGDLU1PVQE"):
        """
        Initialize MCP server.

        Args:
            kb_id: Knowledge Base ID
        """
        self.kb_id = kb_id
        self.retriever = BedrockKBRetriever(kb_id=kb_id)
        logger.info(f"Initialized Bedrock KB MCP Server (KB ID: {kb_id})")

    def get_tools(self) -> List:
        """
        Get list of available LangChain tools.

        Returns:
            List of tool functions decorated with @tool
        """
        return [get_esg_knowledge, search_esg_documents]

    def get_tool_descriptions(self) -> List[Dict[str, str]]:
        """
        Get descriptions of available tools.

        Returns:
            List of dicts with tool names and descriptions
        """
        return [
            {
                "name": "get_esg_knowledge",
                "description": get_esg_knowledge.description
            },
            {
                "name": "search_esg_documents",
                "description": search_esg_documents.description
            }
        ]


def create_mcp_server(kb_id: str = "HGDLU1PVQE") -> BedrockKBMCPServer:
    """
    Factory function to create MCP server instance.

    Args:
        kb_id: Knowledge Base ID

    Returns:
        Initialized BedrockKBMCPServer instance
    """
    return BedrockKBMCPServer(kb_id=kb_id)
