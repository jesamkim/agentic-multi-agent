"""
Strands Agents - Planner + Executor Multi-Agent System with Clarification Loop

Advanced multi-agent ESG chatbot architecture:
- Supervisor V2: Intelligent orchestrator with clarification loop
- Planner Agent: Analyzes questions and creates execution plans
- Executor: Interprets and executes plans
- ESG Agent: Samsung C&T knowledge specialist
- Research Agent: External ESG information specialist
- Aggregator Agent: Data synthesis and comparison
"""

# Core models
from .plan_models import (
    StepType, ExecutionStep, ExecutionPlan,
    ClarificationQuestion, ClarificationRequest,
    StepResult, ExecutionResult
)

# Specialist agents
from .esg_agent import esg_agent, create_esg_agent, ESG_SYSTEM_PROMPT
from .research_agent import (
    research_agent,
    create_research_agent,
    research_multiple_companies,
    RESEARCH_SYSTEM_PROMPT
)
from .aggregator_agent import (
    aggregator_agent,
    create_aggregator_agent,
    aggregate_and_compare,
    AGGREGATOR_SYSTEM_PROMPT
)
from .report_agent import (
    report_agent,
    create_report_agent,
    REPORT_SYSTEM_PROMPT
)

# Planning and execution
from .planner_agent import (
    planner_agent,
    create_planner_agent,
    create_plan,
    PLANNER_SYSTEM_PROMPT
)
from .executor_agent import (
    Executor,
    get_executor,
    execute_plan
)

# Main orchestrator (V2 with Planner-Executor + Clarification)
from .supervisor_agent_v2 import (
    supervisor_agent,
    create_supervisor_v2,
    call_esg_agent,
    call_research_agent,
    create_and_execute_plan,
    SUPERVISOR_V2_SYSTEM_PROMPT
)

__all__ = [
    # Models
    'StepType',
    'ExecutionStep',
    'ExecutionPlan',
    'ClarificationQuestion',
    'ClarificationRequest',
    'StepResult',
    'ExecutionResult',
    # Specialist agents
    'esg_agent',
    'research_agent',
    'aggregator_agent',
    'report_agent',
    'create_esg_agent',
    'create_research_agent',
    'create_aggregator_agent',
    'create_report_agent',
    # Planning and execution
    'planner_agent',
    'create_planner_agent',
    'create_plan',
    'Executor',
    'get_executor',
    'execute_plan',
    # Orchestrator
    'supervisor_agent',
    'create_supervisor_v2',
    # A2A tools
    'call_esg_agent',
    'call_research_agent',
    'create_and_execute_plan',
    'generate_report_for_analysis',
    # Helper functions
    'research_multiple_companies',
    'aggregate_and_compare',
    # System prompts
    'ESG_SYSTEM_PROMPT',
    'RESEARCH_SYSTEM_PROMPT',
    'AGGREGATOR_SYSTEM_PROMPT',
    'REPORT_SYSTEM_PROMPT',
    'PLANNER_SYSTEM_PROMPT',
    'SUPERVISOR_V2_SYSTEM_PROMPT'
]
