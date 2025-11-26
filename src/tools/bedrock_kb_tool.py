"""
Bedrock Knowledge Base Tools for Strands Agents

Provides tools to retrieve knowledge from enterprise
sustainability reports via AWS Bedrock Knowledge Base.
"""

import boto3
import logging
from typing import List, Dict, Any
from strands import tool

logger = logging.getLogger(__name__)


class BedrockKBRetriever:
    """Bedrock Knowledge Base retriever for sustainability information."""
    
    def __init__(
        self,
        kb_id: str = "HGDLU1PVQE",
        region: str = "us-west-2",
        profile: str = "profile2"
    ):
        """
        Initialize Bedrock KB retriever.
        
        Args:
            kb_id: Knowledge Base ID
            region: AWS region
            profile: AWS profile name
        """
        self.kb_id = kb_id
        self.region = region
        
        # Create Bedrock Agent Runtime client
        session = boto3.Session(
            profile_name=profile,
            region_name=region
        )
        self.client = session.client('bedrock-agent-runtime')
        logger.info(f"Initialized Bedrock KB retriever (KB ID: {kb_id})")
    
    def retrieve(
        self,
        query: str,
        num_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve knowledge from Bedrock KB.
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of retrieved documents with content and metadata
        """
        try:
            logger.info(f"Retrieving from KB: {query[:100]}...")
            
            response = self.client.retrieve(
                knowledgeBaseId=self.kb_id,
                retrievalQuery={'text': query},
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': num_results,
                        'overrideSearchType': 'HYBRID'
                    }
                }
            )
            
            results = response.get('retrievalResults', [])
            logger.info(f"Retrieved {len(results)} results")
            
            # Format results
            formatted_results = []
            for idx, result in enumerate(results, 1):
                content = result.get('content', {}).get('text', '')
                score = result.get('score', 0.0)
                location = result.get('location', {})
                
                formatted_results.append({
                    'rank': idx,
                    'content': content,
                    'score': score,
                    'location': location
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"KB retrieval failed: {str(e)}")
            raise


# Global retriever instance
_retriever = None


def get_retriever() -> BedrockKBRetriever:
    """Get or create retriever instance."""
    global _retriever
    if _retriever is None:
        _retriever = BedrockKBRetriever()
    return _retriever


@tool
def get_esg_knowledge(query: str, num_results: int = 10) -> str:
    """
    Retrieve knowledge from enterprise sustainability reports.

    Use this tool to find information about:
    - Environmental initiatives and carbon emissions
    - Social responsibility and employee welfare
    - Governance structure and policies
    - Sustainability goals and achievements
    - Performance metrics and data

    Args:
        query: Search query about sustainability practices
        num_results: Number of results to retrieve (default: 10)

    Returns:
        Formatted search results from the knowledge base
    """
    try:
        retriever = get_retriever()
        results = retriever.retrieve(query, num_results)
        
        # Format for LLM consumption
        if not results:
            return f"No information found for query: {query}"
        
        formatted = f"Knowledge Base Results for: {query}\n\n"
        for result in results:
            formatted += f"[Result {result['rank']}] (Score: {result['score']:.3f})\n"
            formatted += f"{result['content']}\n\n"
        
        return formatted
        
    except Exception as e:
        return f"Error retrieving knowledge: {str(e)}"


__all__ = ['BedrockKBRetriever', 'get_retriever', 'get_esg_knowledge']
