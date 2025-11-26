"""
Report Generation Agent

Specialized agent for generating HTML report sections.
Used by stepwise append approach - generates one section at a time.
"""

from strands import Agent
import logging

logger = logging.getLogger(__name__)


REPORT_SYSTEM_PROMPT = """You are an HTML report section generator for sustainability analysis.

**Your role:**
Generate ONLY the requested section in pure HTML format.

**CRITICAL OUTPUT FORMAT:**
- Output ONLY HTML tags - NO code block markers
- DO NOT wrap output in ```html ... ```
- DO NOT use Markdown syntax (no ##, **, -, etc.)
- Start directly with <h2> tag
- Pure HTML tags only: <h2>, <h3>, <p>, <table>, <ul>, <li>, <strong>

**LANGUAGE:**
- ALWAYS write in KOREAN (한글)
- Technical terms can include English in parentheses
- Example: "탄소배출량(Carbon Emissions)"

**Section types you'll be asked to generate:**
1. Executive Summary - 2-3 substantial paragraphs in KOREAN
2. Detailed Analysis - Multiple subsections with tables in KOREAN
3. Conclusions and Recommendations - Summary in KOREAN

**Important:**
- Generate ONLY the section requested (not full report)
- Use proper HTML structure
- Be comprehensive and professional
- KOREAN language required
- NO code block markers
- Your output will be appended to an HTML file"""


def create_report_agent(
    model: str = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"
) -> Agent:
    """
    Create Report Section Generator Agent.

    Generates individual HTML sections (not full reports).
    Used by stepwise append approach.

    Args:
        model: Bedrock model ID

    Returns:
        Configured Report Agent
    """
    agent = Agent(
        model=model,
        tools=[],  # No tools - pure HTML section generation
        system_prompt=REPORT_SYSTEM_PROMPT
    )

    logger.info(f"Created Report Section Agent with model: {model}")
    return agent


def create_report_with_fallback(prompt: str) -> str:
    """
    Generate report with Sonnet, fallback to Haiku on timeout.

    Args:
        prompt: Report generation prompt

    Returns:
        Generated report content
    """
    # Primary: Claude Sonnet 4.5
    try:
        logger.info("Generating report with Claude Sonnet 4.5...")
        agent_sonnet = create_report_agent(
            model="global.anthropic.claude-sonnet-4-5-20250929-v1:0"
        )
        response = agent_sonnet(prompt)
        logger.info("Report generated with Sonnet")
        return str(response)

    except Exception as e:
        error_msg = str(e)

        # Check if timeout error
        if "Read timed out" in error_msg or "timeout" in error_msg.lower():
            logger.warning(f"Sonnet timeout, falling back to Haiku 4.5: {error_msg}")

            try:
                # Fallback: Claude Haiku 4.5 (faster)
                agent_haiku = create_report_agent(
                    model="global.anthropic.claude-haiku-4-5-20251001-v1:0"
                )
                response = agent_haiku(prompt)
                logger.info("Report generated with Haiku 4.5 (fallback)")
                return str(response)

            except Exception as e2:
                logger.error(f"Haiku fallback also failed: {str(e2)}")
                raise Exception(f"Report generation failed with both models: Sonnet timeout, Haiku error: {str(e2)}")

        else:
            # Non-timeout error, re-raise
            raise


# Create default report agent with Haiku 4.5 (faster, no timeout)
report_agent = create_report_agent(
    model="global.anthropic.claude-haiku-4-5-20251001-v1:0"
)


__all__ = [
    'report_agent',
    'create_report_agent',
    'create_report_with_fallback',
    'REPORT_SYSTEM_PROMPT'
]
