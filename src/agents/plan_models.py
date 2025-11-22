"""
Pydantic models for structured execution plans and clarification.

Defines schemas for:
- Execution plans created by Planner Agent
- Clarification requests for unclear questions
- Execution results
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class StepType(str, Enum):
    """Types of execution steps."""
    REASONING = "reasoning"
    WEB_SEARCH = "web_search"
    NEWS_SEARCH = "news_search"
    KB_QUERY = "kb_query"
    AGGREGATE = "aggregate"
    COMPARE = "compare"


class ExecutionStep(BaseModel):
    """A single step in the execution plan."""
    step_id: int = Field(..., description="Sequential step number")
    step_type: StepType = Field(..., description="Type of step to execute")
    description: str = Field(..., description="Human-readable description of what this step does")
    action: str = Field(..., description="Specific action or query to execute")
    dependencies: List[int] = Field(default_factory=list, description="Step IDs that must complete before this step")
    expected_output: str = Field(..., description="Expected output format or content")


class ExecutionPlan(BaseModel):
    """Complete execution plan for answering a user question."""
    question: str = Field(..., description="Original user question")
    analysis: str = Field(..., description="Analysis of the question and required approach")
    steps: List[ExecutionStep] = Field(..., description="Ordered list of execution steps", max_length=15)
    expected_final_output: str = Field(..., description="Description of final answer format")
    complexity: str = Field(..., description="Question complexity: simple, medium, complex")

    def validate_step_count(self) -> bool:
        """
        Validate step count based on complexity.

        Returns:
            True if step count is appropriate for complexity
        """
        limits = {
            'simple': 5,
            'medium': 10,
            'complex': 15
        }

        max_steps = limits.get(self.complexity, 15)
        return len(self.steps) <= max_steps

    def get_max_steps_for_complexity(self) -> int:
        """Get maximum allowed steps for this plan's complexity."""
        limits = {
            'simple': 5,
            'medium': 10,
            'complex': 15
        }
        return limits.get(self.complexity, 15)


class ClarificationQuestion(BaseModel):
    """A single clarification question."""
    question: str = Field(..., description="Question to ask the user")
    reason: str = Field(..., description="Why this clarification is needed")
    examples: Optional[List[str]] = Field(default=None, description="Example answers to help user")


class ClarificationRequest(BaseModel):
    """Request for clarifying an unclear question."""
    original_question: str = Field(..., description="Original user question")
    unclear_aspects: List[str] = Field(..., description="What aspects are unclear")
    clarification_questions: List[ClarificationQuestion] = Field(..., description="Questions to ask user")
    suggestion: Optional[str] = Field(default=None, description="Suggested interpretation if applicable")


class StepResult(BaseModel):
    """Result of executing a single step."""
    step_id: int
    step_type: StepType
    status: str = Field(..., description="success, failed, skipped")
    output: str = Field(default="", description="Result data from step execution")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    execution_time: Optional[float] = Field(default=None, description="Execution time in seconds")


class ExecutionResult(BaseModel):
    """Complete result of executing a plan."""
    plan: ExecutionPlan
    step_results: List[StepResult]
    final_answer: str
    total_execution_time: float
    success_rate: float = Field(..., description="Percentage of steps completed successfully")


__all__ = [
    'StepType',
    'ExecutionStep',
    'ExecutionPlan',
    'ClarificationQuestion',
    'ClarificationRequest',
    'StepResult',
    'ExecutionResult'
]
