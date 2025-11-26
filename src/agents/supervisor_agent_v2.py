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
from src.tools.report_tools import _generate_report_internal
import logging

logger = logging.getLogger(__name__)


SUPERVISOR_V2_SYSTEM_PROMPT = """You are an intelligent supervisor for an agentic AI chatbot system.

**CONVERSATION CONTEXT:**
You will receive conversation history in this format:
```
Previous Q: [question]
Previous A: [answer]

Current question: [question]
```

Use previous answers as context for current question.

**CRITICAL for Report Requests:**
When user says "보고서 만들어줘" (make report) after a previous discussion:
1. Extract the topic from previous question
2. Extract the previous answer as data source
3. Call: create_detailed_report(topic="[topic from previous Q]", previous_analysis="[previous A]")

The previous_analysis parameter should contain the full previous answer that provides context.

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

2. Report generation (이전 답변 활용):
   - Keywords: "보고서", "리포트", "PDF", "문서"

   **CRITICAL: Use existing answer, DO NOT re-collect data**

   When user requests report AFTER a previous discussion:

   ✓ DO:
   1. Find previous answer in conversation history (Previous A)
   2. Extract topic from previous question (Previous Q)
   3. Call: create_detailed_report(topic="...", previous_analysis="Previous A")

   ✗ DON'T:
   - Call call_esg_agent again
   - Call call_research_agent again
   - Call create_and_execute_plan again
   - Re-collect or re-query any data

   The report tool will generate HTML/PDF from existing answer.
   Previous answer contains all necessary data.

3. Single-source questions (brief answer):
   - Internal knowledge: "탄소배출량은?"
   → Use call_esg_agent (returns 3-5 sentence summary)
   - External information: "회사 A의 지속가능성 보고서"
   → Use call_research_agent (returns brief summary)

4. Complex multi-step questions (brief answer with report option):
   - Comparisons: "회사 A와 회사 B의 LTIR 비교"
   - Multiple companies: "주요 회사들의 안전 성과"
   - Multi-source analysis: "업계 벤치마킹"
   → Use create_and_execute_plan (returns concise summary + "상세 보고서 필요시 요청" 안내)

**Key Decision Rules:**
- If question mentions specific company names → clear
- If question says "주요" without naming companies → unclear, ask for specifics
- If comparison without all entities specified → unclear
- If timeframe needed but not specified → clarify

Always maintain professional tone and answer in user's language."""


@tool
def call_esg_agent(query: str) -> str:
    """Call Knowledge Agent for internal knowledge base questions."""
    logger.info(f"Delegating to Knowledge Agent: {query[:100]}...")
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
    Generate HTML/PDF report from EXISTING conversation data.

    CRITICAL: This tool uses ONLY the previous answer from conversation history.
    DO NOT collect new data. DO NOT call other agents again.

    When to use:
    - User says "보고서 만들어줘" AFTER receiving an answer
    - Extract previous answer from conversation history
    - Pass it as previous_analysis parameter

    When NOT to use:
    - User asks for report WITHOUT previous discussion
    - No previous answer in history

    Args:
        topic: Report title (extract from previous question)
        previous_analysis: REQUIRED - Full text of previous answer

    Returns:
        Message with HTML and PDF file paths

    Example usage:
    Previous Q: "삼성물산 지속가능성 공시 의무는?"
    Previous A: [Full answer about disclosure requirements]
    Current Q: "보고서 만들어줘"
    → Call: create_detailed_report(topic="...", previous_analysis="[Previous A]")
    """
    logger.info(f"Creating detailed report: {topic[:100]}...")

    try:
        # Check if previous analysis exists
        if not previous_analysis:
            logger.warning("No previous_analysis provided - cannot generate report")
            return """보고서를 생성하려면 먼저 관련 질문을 해주세요.

예시:
1. "삼성물산 산림벌채 리스크 분석" 질문 → 데이터 조회 및 답변
2. "보고서 만들어줘" 요청 → 이전 답변 기반 보고서 생성

보고서는 이전 대화의 답변을 활용하여 생성됩니다."""

        # Generate report step-by-step with HTML append (timeout prevention)
        # _generate_report_internal will use generate_report_stepwise_append
        logger.info("Generating report step-by-step...")
        result = _generate_report_internal(
            topic=topic,
            analysis_data=previous_analysis
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
