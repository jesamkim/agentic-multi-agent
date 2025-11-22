"""
Planner Agent - Strands Agents Implementation

Analyzes user questions and creates structured execution plans
for complex multi-step queries.
"""

from strands import Agent
from .plan_models import ExecutionPlan, ExecutionStep, StepType
import logging
import json

logger = logging.getLogger(__name__)


PLANNER_SYSTEM_PROMPT = """You are an expert planner for an ESG information system.

Your role is to analyze user questions and create detailed execution plans.

**Available Resources:**
1. Bedrock Knowledge Base - Samsung C&T 2025 Sustainability Report (124 pages)
2. Web Search - General ESG information and other companies
3. News Search - Recent ESG news and updates

**Question Analysis Process:**
1. Understand what the user is asking
2. Identify required information sources
3. Break down into executable steps
4. Define dependencies between steps
5. Specify expected outputs

**Step Types:**
- reasoning: Analyze concepts, define terms, identify entities
- web_search: Search web for general information
- news_search: Search for recent news
- kb_query: Query Samsung C&T knowledge base
- aggregate: Collect and organize results
- compare: Compare data from multiple sources

**Complex Question Handling:**
Example: "삼성물산 LTIR과 주요 건설사 LTIR 비교"

Plan:
1. reasoning: Define LTIR (Lost Time Injury Rate)
2. reasoning: Identify major construction companies (GS, Daelim, Hyundai, etc.)
3. web_search: Search LTIR for GS E&C
4. web_search: Search LTIR for Daelim
5. web_search: Search LTIR for Hyundai E&C
6. kb_query: Retrieve Samsung C&T LTIR data
7. aggregate: Collect all LTIR data
8. compare: Analyze and compare safety performance

**Important - Step Count Limits (MANDATORY):**
- Simple questions: MAX 5 steps
- Medium questions: MAX 10 steps
- Complex questions: MAX 15 steps
- NEVER exceed these limits - prioritize most important steps
- For comparison questions, limit to 3-4 companies max
- Always specify clear dependencies

**Output Format:**
You MUST output a valid JSON ExecutionPlan following this schema:
{
  "question": "original user question",
  "analysis": "your analysis of the question",
  "steps": [
    {
      "step_id": 1,
      "step_type": "reasoning",
      "description": "Define LTIR metric",
      "action": "Explain what LTIR means and how it's calculated",
      "dependencies": [],
      "expected_output": "LTIR definition and calculation method"
    },
    ...
  ],
  "expected_final_output": "description of final answer",
  "complexity": "simple|medium|complex"
}

Be thorough and create comprehensive plans for complex questions."""


def create_planner_agent(
    model: str = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"
) -> Agent:
    """
    Create Planner Agent that outputs JSON plans.

    Args:
        model: Bedrock model ID

    Returns:
        Configured Planner Agent
    """
    agent = Agent(
        model=model,
        tools=[],  # Planner doesn't use tools, just thinks
        system_prompt=PLANNER_SYSTEM_PROMPT
    )

    logger.info(f"Created Planner Agent with model: {model}")
    return agent


def create_plan(question: str) -> ExecutionPlan:
    """
    Create execution plan for a question.

    Args:
        question: User question

    Returns:
        ExecutionPlan object with structured steps
    """
    planner = create_planner_agent()

    logger.info(f"Creating plan for: {question[:100]}...")

    # Invoke planner to get JSON response
    response = planner(question)
    response_text = str(response)

    # Parse JSON response to ExecutionPlan
    try:
        # Extract JSON from response (may be wrapped in markdown code blocks)
        json_text = response_text
        if "```json" in json_text:
            json_text = json_text.split("```json")[1].split("```")[0].strip()
        elif "```" in json_text:
            json_text = json_text.split("```")[1].split("```")[0].strip()

        plan_dict = json.loads(json_text)
        plan = ExecutionPlan(**plan_dict)

        logger.info(f"Created plan with {len(plan.steps)} steps")
        return plan

    except Exception as e:
        logger.error(f"Failed to parse plan: {str(e)}")
        logger.error(f"Response was: {response_text[:500]}...")

        # Fallback: create simple plan
        return ExecutionPlan(
            question=question,
            analysis="Failed to create detailed plan, using fallback",
            steps=[
                ExecutionStep(
                    step_id=1,
                    step_type=StepType.WEB_SEARCH,
                    description="Search for information",
                    action=question,
                    dependencies=[],
                    expected_output="Search results"
                )
            ],
            expected_final_output="Answer to user question",
            complexity="simple"
        )


# Create default planner
planner_agent = create_planner_agent()


__all__ = [
    'planner_agent',
    'create_planner_agent',
    'create_plan',
    'PLANNER_SYSTEM_PROMPT'
]
