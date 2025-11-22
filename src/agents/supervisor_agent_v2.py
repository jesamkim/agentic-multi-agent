"""
Supervisor Agent V2 - Planner + Executor + Clarification Loop

Advanced orchestrator with:
1. Clarification loop for unclear questions
2. Planner-Executor pattern for complex questions
3. Direct delegation for simple questions
"""

from strands import Agent, tool
from .planner_agent import create_plan
from .executor_agent import execute_plan
from .esg_agent import esg_agent
from .research_agent import research_agent
from src.tools.report_tools import _generate_report_internal  # Internal function
import logging

logger = logging.getLogger(__name__)


SUPERVISOR_V2_SYSTEM_PROMPT = """You are an intelligent supervisor for an ESG chatbot system.

**EFFICIENCY GUIDELINES:**
- Minimize clarification questions (1-2 questions max if really needed)
- Make reasonable assumptions when minor details unclear
- Only ask for clarification if critical information is missing

**STEP 1: Check Question Clarity (Be Lenient)**

First, assess if question is answerable:

ONLY ask for clarification if:
- Multiple companies mentioned but identities completely unclear
- Core metric/topic is ambiguous
- Cannot proceed without the information

MAKE REASONABLE ASSUMPTIONS for:
- "주요 회사" → Top 3-5 by market cap
- "최근" → Last year (2023-2024)
- "어느 정도" → Compare with industry average

If truly critical info missing, respond with:
"CLARIFICATION_NEEDED:
1. [ONE critical question]
2. [ONLY if absolutely necessary]"

If answerable with assumptions, proceed to STEP 2.

**STEP 2: Classify Question Type**

1. Simple questions (direct response):
   - Greetings: "안녕하세요"
   - Thanks: "고마워요"
   - System questions: "What can you do?"
   → Respond directly (friendly, brief)

2. Report generation requests:
   - "보고서 만들어줘"
   - "상세 리포트 작성해줘"
   - "PDF로 저장해줘"
   - "자세한 분석 문서"
   → Use create_detailed_report

3. Single-source questions (brief answer):
   - Samsung C&T only: "삼성물산의 탄소배출량은?"
   → Use call_esg_agent (returns 3-5 sentence summary)
   - Other company only: "현대자동차 ESG 보고서"
   → Use call_research_agent (returns brief summary)

4. Complex multi-step questions (brief answer with report option):
   - Comparisons: "삼성물산과 GS건설 LTIR 비교"
   - Multiple companies: "주요 건설사들의 안전 성과"
   - Multi-source analysis: "국내외 건설사 ESG 벤치마킹"
   → Use create_and_execute_plan (returns concise summary + "상세 보고서 필요시 요청" 안내)

**Key Decision Rules:**
- If question mentions specific company names → clear
- If question says "주요" without naming companies → unclear, ask for specifics
- If comparison without all entities specified → unclear
- If timeframe needed but not specified → clarify

Always maintain professional tone and answer in user's language."""


@tool
def call_esg_agent(query: str) -> str:
    """Call ESG Agent for Samsung C&T questions."""
    logger.info(f"Delegating to ESG Agent: {query[:100]}...")
    response = esg_agent(query)
    return str(response)


@tool
def call_research_agent(query: str) -> str:
    """Call Research Agent for external information."""
    logger.info(f"Delegating to Research Agent: {query[:100]}...")
    response = research_agent(query)
    return str(response)


@tool
def create_and_execute_plan(query: str) -> str:
    """
    Create and execute multi-step plan for complex questions.

    Automatically enhances query to ensure concise output.
    Always suggests detailed report option.
    """
    logger.info(f"Creating plan for complex question: {query[:100]}...")

    try:
        # Enhance query to enforce conciseness
        enhanced_query = f"""{query}

답변 요구사항:
- 핵심 내용만 5-6문장으로 간결하게 요약
- 가장 중요한 결론 1-2가지만 강조
- 불필요한 세부사항 제외"""

        logger.info("Query enhanced for concise output")

        plan = create_plan(enhanced_query)
        logger.info(f"Plan created with {len(plan.steps)} steps")

        result = execute_plan(plan)
        logger.info(
            f"Plan executed: {result.success_rate:.1f}% success "
            f"in {result.total_execution_time:.2f}s"
        )

        # Always add report suggestion for complex queries
        answer = result.final_answer
        answer += "\n\n💡 더 상세한 분석이 필요하시면 '상세 보고서 작성해줘'라고 요청해주세요."

        return answer

    except Exception as e:
        logger.error(f"Plan execution failed: {str(e)}")
        return f"Error executing plan: {str(e)}"


@tool
def create_detailed_report(topic: str, previous_analysis: str = "") -> str:
    """
    Generate detailed HTML/PDF report for ESG analysis.

    Use this when user explicitly requests:
    - "보고서 만들어줘"
    - "상세 리포트 작성"
    - "PDF로 저장"
    - "자세한 분석 문서"

    Args:
        topic: Report topic
        previous_analysis: Previous chat analysis to expand into report

    Returns:
        Message with file paths for HTML and PDF
    """
    logger.info(f"Creating detailed report: {topic[:100]}...")

    try:
        # Prepare analysis data
        if previous_analysis:
            analysis_data = f"<h2>{topic}</h2>\n\n{previous_analysis}"
        else:
            # Use research agent to gather fresh data
            logger.info("No previous analysis, gathering fresh data...")
            research_response = research_agent(f"Comprehensive information about: {topic}")
            analysis_data = f"<h2>{topic}</h2>\n\n{str(research_response)}"

        # Call internal function directly (not decorated tool)
        result = _generate_report_internal(
            topic=topic,
            analysis_data=analysis_data
        )

        return result

    except Exception as e:
        logger.error(f"Report generation failed: {str(e)}")
        return f"보고서 생성 중 오류 발생: {str(e)}"


def create_supervisor_v2(
    model: str = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"
) -> Agent:
    """
    Create Supervisor Agent V2 with Clarification Loop and Report Generation.

    Args:
        model: Bedrock model ID

    Returns:
        Configured Supervisor Agent
    """
    agent = Agent(
        model=model,
        tools=[
            call_esg_agent,
            call_research_agent,
            create_and_execute_plan,
            create_detailed_report  # HTML + PDF generation
        ],
        system_prompt=SUPERVISOR_V2_SYSTEM_PROMPT
    )

    logger.info(f"Created Supervisor V2 Agent with model: {model}")
    return agent


# Create default supervisor
supervisor_agent = create_supervisor_v2()


__all__ = [
    'supervisor_agent',
    'create_supervisor_v2',
    'call_esg_agent',
    'call_research_agent',
    'create_and_execute_plan',
    'create_detailed_report',
    'SUPERVISOR_V2_SYSTEM_PROMPT'
]
