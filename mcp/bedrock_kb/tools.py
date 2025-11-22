"""
Bedrock Knowledge Base retrieval tools for MCP server.

This module provides functions to retrieve information from AWS Bedrock Knowledge Base
using hybrid search (keyword + semantic).
"""

import boto3
from botocore.exceptions import ClientError
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class BedrockKBRetriever:
    """
    Bedrock Knowledge Base retrieval client.

    Provides hybrid search capabilities over the knowledge base with configurable
    number of results and search parameters.
    """

    def __init__(
        self,
        kb_id: str = "HGDLU1PVQE",
        profile_name: str = "profile2",
        region_name: str = "us-west-2"
    ):
        """
        Initialize Bedrock KB retriever.

        Args:
            kb_id: Knowledge Base ID
            profile_name: AWS profile name
            region_name: AWS region
        """
        self.kb_id = kb_id
        self.profile_name = profile_name
        self.region_name = region_name

        session = boto3.Session(
            profile_name=profile_name,
            region_name=region_name
        )
        self.bedrock_agent_runtime = session.client('bedrock-agent-runtime')

        logger.info(
            f"Initialized Bedrock KB Retriever (KB ID: {kb_id}, "
            f"Region: {region_name}, Profile: {profile_name})"
        )

    def retrieve(
        self,
        query: str,
        num_results: int = 10,
        search_type: str = "HYBRID"
    ) -> List[Dict]:
        """
        Retrieve documents from Knowledge Base using hybrid search.

        Args:
            query: Search query text
            num_results: Number of results to return (default: 10)
            search_type: Search type - "HYBRID", "SEMANTIC", or "KEYWORD" (default: "HYBRID")

        Returns:
            List of retrieved documents with content, metadata, and scores

        Raises:
            ClientError: If Bedrock API call fails
            ValueError: If invalid parameters provided
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        if num_results < 1 or num_results > 100:
            raise ValueError("num_results must be between 1 and 100")

        if search_type not in ["HYBRID", "SEMANTIC", "KEYWORD"]:
            raise ValueError(
                "search_type must be one of: HYBRID, SEMANTIC, KEYWORD"
            )

        try:
            logger.info(
                f"Retrieving from KB (query: '{query[:50]}...', "
                f"num_results: {num_results}, search_type: {search_type})"
            )

            response = self.bedrock_agent_runtime.retrieve(
                knowledgeBaseId=self.kb_id,
                retrievalQuery={'text': query},
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': num_results,
                        'overrideSearchType': search_type
                    }
                }
            )

            results = response.get('retrievalResults', [])
            logger.info(f"Retrieved {len(results)} results from KB")

            return self._format_results(results)

        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(
                f"Bedrock API error: {error_code} - {error_message}"
            )
            raise
        except Exception as e:
            logger.error(f"Unexpected error during retrieval: {str(e)}")
            raise

    def retrieve_and_generate(
        self,
        query: str,
        model_id: str = "global.anthropic.claude-sonnet-4-5-20250929-v1:0",
        num_results: int = 10
    ) -> Dict:
        """
        Retrieve documents and generate answer using Bedrock model.

        This is a convenience method that combines retrieval and generation
        in a single API call.

        Args:
            query: Search query text
            model_id: Bedrock model ID to use for generation
            num_results: Number of results to retrieve

        Returns:
            Dict containing generated answer, citations, and retrieved documents

        Raises:
            ClientError: If Bedrock API call fails
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        try:
            logger.info(
                f"Retrieve and generate (query: '{query[:50]}...', "
                f"model: {model_id})"
            )

            model_arn = f"arn:aws:bedrock:{self.region_name}::foundation-model/{model_id}"

            response = self.bedrock_agent_runtime.retrieve_and_generate(
                input={'text': query},
                retrieveAndGenerateConfiguration={
                    'type': 'KNOWLEDGE_BASE',
                    'knowledgeBaseConfiguration': {
                        'knowledgeBaseId': self.kb_id,
                        'modelArn': model_arn,
                        'retrievalConfiguration': {
                            'vectorSearchConfiguration': {
                                'numberOfResults': num_results,
                                'overrideSearchType': 'HYBRID'
                            }
                        }
                    }
                }
            )

            output = response.get('output', {}).get('text', '')
            citations = response.get('citations', [])

            logger.info(
                f"Generated answer (length: {len(output)}, "
                f"citations: {len(citations)})"
            )

            return {
                'answer': output,
                'citations': citations,
                'session_id': response.get('sessionId')
            }

        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(
                f"Bedrock API error: {error_code} - {error_message}"
            )
            raise
        except Exception as e:
            logger.error(f"Unexpected error during retrieve_and_generate: {str(e)}")
            raise

    def _format_results(self, results: List[Dict]) -> List[Dict]:
        """
        Format raw Bedrock results into standardized structure.

        Args:
            results: Raw results from Bedrock API

        Returns:
            Formatted list of results with content, metadata, and scores
        """
        formatted = []

        for result in results:
            content = result.get('content', {}).get('text', '')
            score = result.get('score', 0.0)
            location = result.get('location', {})
            metadata = result.get('metadata', {})

            formatted.append({
                'content': content,
                'score': score,
                'location': location,
                'metadata': metadata,
                's3_uri': location.get('s3Location', {}).get('uri', ''),
                'type': location.get('type', 'UNKNOWN')
            })

        return formatted


def get_esg_knowledge(query: str, num_results: int = 10) -> List[Dict]:
    """
    Retrieve ESG knowledge from Bedrock Knowledge Base.

    This is the main tool function exposed to agents via MCP protocol.

    Args:
        query: User query or question about ESG topics
        num_results: Number of results to return (default: 10)

    Returns:
        List of relevant documents with content and metadata
    """
    retriever = BedrockKBRetriever()
    return retriever.retrieve(query=query, num_results=num_results)


def search_esg_documents(
    query: str,
    search_type: str = "HYBRID",
    num_results: int = 10
) -> List[Dict]:
    """
    Search ESG documents with configurable search type.

    Args:
        query: Search query
        search_type: "HYBRID", "SEMANTIC", or "KEYWORD"
        num_results: Number of results to return

    Returns:
        List of search results
    """
    retriever = BedrockKBRetriever()
    return retriever.retrieve(
        query=query,
        num_results=num_results,
        search_type=search_type
    )
