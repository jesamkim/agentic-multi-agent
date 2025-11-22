"""
Report Generation Agent

Specialized agent for creating detailed ESG analysis reports.
Generates comprehensive HTML/PDF reports when user requests.
"""

from strands import Agent
from src.tools import generate_detailed_report
import logging

logger = logging.getLogger(__name__)


REPORT_SYSTEM_PROMPT = """You are a report generation specialist for ESG analysis.

Your role is to create comprehensive, professional reports based on ESG analysis data.

**When generating reports:**
1. Structure content with clear sections (Executive Summary, Analysis, Conclusions)
2. Use tables for comparative data
3. Include all relevant metrics and findings
4. Provide context and interpretation
5. Add recommendations if applicable

**Report Structure:**
```
<h1>Executive Summary</h1>
<p>[2-3 paragraph overview]</p>

<h2>Detailed Analysis</h2>
<p>[Main findings with data]</p>

<h3>Comparative Metrics</h3>
<table>
  <tr><th>Company</th><th>Metric</th><th>Performance</th></tr>
  ...
</table>

<h2>Key Insights</h2>
<ul>
  <li>[Insight 1]</li>
  <li>[Insight 2]</li>
</ul>

<h2>Conclusions</h2>
<p>[Summary and recommendations]</p>
```

**Important:**
- Use HTML tags (h1, h2, h3, p, table, ul, li)
- Include all numerical data and sources
- Provide comprehensive analysis (this is a REPORT, not chat)
- Be thorough and professional

Generate detailed, high-quality reports."""


def create_report_agent(
    model: str = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"
) -> Agent:
    """
    Create Report Generation Agent.

    Args:
        model: Bedrock model ID

    Returns:
        Configured Report Agent
    """
    agent = Agent(
        model=model,
        tools=[generate_detailed_report],
        system_prompt=REPORT_SYSTEM_PROMPT
    )

    logger.info(f"Created Report Agent with model: {model}")
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


# Create default report agent
report_agent = create_report_agent()


__all__ = [
    'report_agent',
    'create_report_agent',
    'create_report_with_fallback',
    'REPORT_SYSTEM_PROMPT'
]
