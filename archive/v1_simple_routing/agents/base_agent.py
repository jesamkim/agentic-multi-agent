"""
Base Agent class for all agents in the chatbot system.

Provides common functionality for LLM interaction, tool usage,
and conversation management using AWS Bedrock Claude Sonnet 4.5.
"""

from langchain_aws import ChatBedrock
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import List, Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)


class BaseAgent:
    """
    Base agent class with Bedrock Claude Sonnet 4.5 integration.

    All specialized agents (Supervisor, ESG, etc.) should inherit from this class.
    """

    # Default model configuration for all agents
    DEFAULT_MODEL_ID = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"
    DEFAULT_REGION = "us-west-2"
    DEFAULT_PROFILE = "profile2"
    DEFAULT_MAX_TOKENS = 8192
    DEFAULT_TEMPERATURE = 0

    def __init__(
        self,
        agent_name: str,
        system_prompt: str,
        tools: Optional[List] = None,
        model_id: Optional[str] = None,
        region: Optional[str] = None,
        profile: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ):
        """
        Initialize base agent.

        Args:
            agent_name: Name of the agent
            system_prompt: System prompt defining agent behavior
            tools: List of LangChain tools available to agent
            model_id: Bedrock model ID (default: Claude Sonnet 4.5)
            region: AWS region
            profile: AWS profile name
            max_tokens: Maximum tokens for response
            temperature: Model temperature (0 = deterministic)
            **kwargs: Additional model parameters
        """
        self.agent_name = agent_name
        self.system_prompt = system_prompt
        self.tools = tools or []

        # Model configuration
        self.model_id = model_id or self.DEFAULT_MODEL_ID
        self.region = region or self.DEFAULT_REGION
        self.profile = profile or self.DEFAULT_PROFILE
        self.max_tokens = max_tokens or self.DEFAULT_MAX_TOKENS
        self.temperature = temperature or self.DEFAULT_TEMPERATURE

        # Initialize LLM
        self.llm = self._create_llm(**kwargs)

        # Initialize agent if tools are provided
        self.agent = None
        self.agent_executor = None
        if self.tools:
            self._create_agent()

        logger.info(
            f"Initialized {agent_name} "
            f"(model: {self.model_id}, tools: {len(self.tools)})"
        )

    def _create_llm(self, **kwargs) -> ChatBedrock:
        """
        Create ChatBedrock LLM instance.

        Args:
            **kwargs: Additional model parameters

        Returns:
            Configured ChatBedrock instance
        """
        model_kwargs = {
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            **kwargs
        }

        llm = ChatBedrock(
            model_id=self.model_id,
            region_name=self.region,
            credentials_profile_name=self.profile,
            model_kwargs=model_kwargs
        )

        logger.debug(
            f"Created LLM: {self.model_id} "
            f"(max_tokens={self.max_tokens}, temperature={self.temperature})"
        )

        return llm

    def _create_agent(self):
        """
        Create LangChain agent with tools.

        Creates a tool-calling agent with the system prompt and provided tools.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        self.agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )

        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )

        logger.debug(f"Created agent executor for {self.agent_name}")

    def invoke(
        self,
        user_input: str,
        chat_history: Optional[List] = None
    ) -> Dict[str, Any]:
        """
        Invoke agent with user input.

        Args:
            user_input: User query or message
            chat_history: Optional conversation history

        Returns:
            Dict containing agent response and metadata
        """
        if self.agent_executor:
            # Use agent with tools
            result = self.agent_executor.invoke({
                "input": user_input,
                "chat_history": chat_history or []
            })

            # Extract output and handle different response formats
            output = result.get("output", "")
            output = self._extract_text_from_response(output)

            return {
                "output": output,
                "intermediate_steps": result.get("intermediate_steps", [])
            }
        else:
            # Direct LLM call without tools
            messages = []
            if self.system_prompt:
                messages.append(("system", self.system_prompt))
            if chat_history:
                messages.extend(chat_history)
            messages.append(("human", user_input))

            response = self.llm.invoke(messages)
            content = self._extract_text_from_response(response.content)

            return {
                "output": content,
                "intermediate_steps": []
            }

    def _extract_text_from_response(self, response) -> str:
        """
        Extract text from various response formats.

        Handles both string responses and Claude's structured responses.

        Args:
            response: Response from LLM (string, list, or dict)

        Returns:
            Extracted text as string
        """
        if isinstance(response, str):
            return response

        if isinstance(response, list):
            # Handle list of content blocks (Claude format)
            texts = []
            for item in response:
                if isinstance(item, dict):
                    if 'text' in item:
                        texts.append(item['text'])
                    elif 'content' in item:
                        texts.append(str(item['content']))
                elif isinstance(item, str):
                    texts.append(item)
            return '\n'.join(texts)

        if isinstance(response, dict):
            # Handle dict response
            if 'text' in response:
                return response['text']
            elif 'content' in response:
                return str(response['content'])

        # Fallback: convert to string
        return str(response)

    async def ainvoke(
        self,
        user_input: str,
        chat_history: Optional[List] = None
    ) -> Dict[str, Any]:
        """
        Async version of invoke.

        Args:
            user_input: User query or message
            chat_history: Optional conversation history

        Returns:
            Dict containing agent response and metadata
        """
        if self.agent_executor:
            result = await self.agent_executor.ainvoke({
                "input": user_input,
                "chat_history": chat_history or []
            })

            # Extract output and handle different response formats
            output = result.get("output", "")
            output = self._extract_text_from_response(output)

            return {
                "output": output,
                "intermediate_steps": result.get("intermediate_steps", [])
            }
        else:
            messages = []
            if self.system_prompt:
                messages.append(("system", self.system_prompt))
            if chat_history:
                messages.extend(chat_history)
            messages.append(("human", user_input))

            response = await self.llm.ainvoke(messages)
            content = self._extract_text_from_response(response.content)

            return {
                "output": content,
                "intermediate_steps": []
            }

    def add_tools(self, tools: List):
        """
        Add tools to agent and recreate agent executor.

        Args:
            tools: List of LangChain tools to add
        """
        self.tools.extend(tools)
        if self.tools:
            self._create_agent()
            logger.info(f"Added {len(tools)} tools to {self.agent_name}")

    def get_info(self) -> Dict[str, Any]:
        """
        Get agent information.

        Returns:
            Dict with agent configuration and status
        """
        return {
            "agent_name": self.agent_name,
            "model_id": self.model_id,
            "region": self.region,
            "num_tools": len(self.tools),
            "tool_names": [tool.name for tool in self.tools],
            "has_agent_executor": self.agent_executor is not None
        }

    def __repr__(self) -> str:
        """String representation of agent."""
        return (
            f"{self.__class__.__name__}("
            f"name='{self.agent_name}', "
            f"model='{self.model_id}', "
            f"tools={len(self.tools)})"
        )
