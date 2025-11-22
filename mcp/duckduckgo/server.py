"""
DuckDuckGo Search MCP Server

Provides web search capabilities through Model Context Protocol.
"""

import json
import logging
from pathlib import Path
from typing import List
from langchain.tools import BaseTool

from .tools import web_search, news_search

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DuckDuckGoMCPServer:
    """
    MCP Server for DuckDuckGo search capabilities.
    """

    def __init__(self):
        """Initialize MCP server with DuckDuckGo tools."""
        self.config = self._load_config()
        self.tools = self._initialize_tools()
        logger.info("DuckDuckGo MCP server initialized")

    def _load_config(self) -> dict:
        """Load configuration from config.json."""
        config_path = Path(__file__).parent / "config.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        logger.info(f"Loaded config: {config['name']} v{config['version']}")
        return config

    def _initialize_tools(self) -> List[BaseTool]:
        """Initialize and return available tools."""
        tools = [web_search, news_search]
        logger.info(f"Initialized {len(tools)} tools: {[t.name for t in tools]}")
        return tools

    def get_tools(self) -> List[BaseTool]:
        """
        Get all available tools.

        Returns:
            List of LangChain tools
        """
        return self.tools

    def get_tool(self, tool_name: str) -> BaseTool:
        """
        Get a specific tool by name.

        Args:
            tool_name: Name of the tool

        Returns:
            LangChain tool

        Raises:
            ValueError: If tool not found
        """
        for tool in self.tools:
            if tool.name == tool_name:
                return tool
        raise ValueError(f"Tool not found: {tool_name}")

    def get_config(self) -> dict:
        """Get server configuration."""
        return self.config


# Global server instance
_server = None


def get_server() -> DuckDuckGoMCPServer:
    """Get or create MCP server instance."""
    global _server
    if _server is None:
        _server = DuckDuckGoMCPServer()
    return _server


def get_tools() -> List[BaseTool]:
    """
    Get all DuckDuckGo search tools.

    Returns:
        List of LangChain tools for web search
    """
    server = get_server()
    return server.get_tools()


# Export for easy import
__all__ = [
    'DuckDuckGoMCPServer',
    'get_server',
    'get_tools'
]
