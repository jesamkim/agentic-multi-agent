"""
Executor Agent - Plan Execution Engine

Interprets and executes structured plans created by Planner Agent.
Orchestrates calls to specialized agents based on execution steps.
"""

from strands import Agent
from .plan_models import (
    ExecutionPlan, ExecutionStep, StepType, 
    StepResult, ExecutionResult
)
from .esg_agent import esg_agent
from .research_agent import research_agent
from .aggregator_agent import aggregator_agent
from typing import Dict, Any, List
import logging
import time
import json

logger = logging.getLogger(__name__)


class Executor:
    """
    Execution engine for running structured plans.
    
    Manages step execution, dependency tracking, and result aggregation.
    """
    
    def __init__(self):
        """Initialize executor with agent references."""
        self.esg_agent = esg_agent
        self.research_agent = research_agent
        self.aggregator_agent = aggregator_agent
        
        # Track step results
        self.step_results: Dict[int, StepResult] = {}
        self.step_outputs: Dict[int, str] = {}
        
        logger.info("Executor initialized")
    
    def execute_plan(self, plan: ExecutionPlan) -> ExecutionResult:
        """
        Execute a complete plan with early termination support.

        Args:
            plan: ExecutionPlan to execute

        Returns:
            ExecutionResult with all step results and final answer
        """
        logger.info(f"Executing plan for: {plan.question}")
        logger.info(f"Plan complexity: {plan.complexity}, Steps: {len(plan.steps)}")

        # Validate step count for complexity
        max_steps = plan.get_max_steps_for_complexity()
        if len(plan.steps) > max_steps:
            logger.warning(
                f"Plan has {len(plan.steps)} steps but complexity '{plan.complexity}' "
                f"allows max {max_steps}. Limiting execution."
            )

        start_time = time.time()

        # Reset state
        self.step_results = {}
        self.step_outputs = {}
        self.early_termination = False

        # Execute steps in order (respecting dependencies)
        for idx, step in enumerate(plan.steps):
            self._execute_step(step, plan)

            # Early termination check after AGGREGATE or COMPARE steps
            if step.step_type in [StepType.AGGREGATE, StepType.COMPARE]:
                if self._check_early_termination(step, plan, idx):
                    logger.info(f"Early termination after step {step.step_id}: sufficient data collected")
                    self.early_termination = True
                    break

        # Generate final answer using aggregator
        final_answer = self._generate_final_answer(plan)

        # Add early termination notice if applicable
        if self.early_termination:
            final_answer += "\n\n(조기 완료: 충분한 정보 수집)"

        total_time = time.time() - start_time

        # Calculate success rate
        successful_steps = sum(
            1 for r in self.step_results.values()
            if r.status == "success"
        )
        success_rate = (successful_steps / len(plan.steps)) * 100

        result = ExecutionResult(
            plan=plan,
            step_results=list(self.step_results.values()),
            final_answer=final_answer,
            total_execution_time=total_time,
            success_rate=success_rate
        )

        logger.info(
            f"Plan executed: {successful_steps}/{len(plan.steps)} steps successful "
            f"({success_rate:.1f}%) in {total_time:.2f}s"
        )

        return result

    def _check_early_termination(
        self,
        current_step: ExecutionStep,
        plan: ExecutionPlan,
        current_index: int
    ) -> bool:
        """
        Check if execution can terminate early.

        Args:
            current_step: Step just completed
            plan: Full execution plan
            current_index: Current step index

        Returns:
            True if early termination recommended
        """
        # Don't terminate if this is the last step
        if current_index >= len(plan.steps) - 1:
            return False

        # Check if we have sufficient data
        current_output = self.step_outputs.get(current_step.step_id, "")

        # Simple heuristic: If output is substantial (>800 chars) after aggregate/compare
        if len(current_output) > 800:
            # Check if remaining steps are all searches (can be skipped)
            remaining_steps = plan.steps[current_index + 1:]
            remaining_are_searches = all(
                s.step_type in [StepType.WEB_SEARCH, StepType.NEWS_SEARCH, StepType.REASONING]
                for s in remaining_steps
            )

            if remaining_are_searches:
                logger.info(f"Sufficient data collected ({len(current_output)} chars), remaining are searches")
                return True

        return False
    
    def _execute_step(self, step: ExecutionStep, plan: ExecutionPlan) -> StepResult:
        """
        Execute a single step.
        
        Args:
            step: Step to execute
            plan: Complete plan (for context)
        
        Returns:
            StepResult
        """
        logger.info(f"Executing step {step.step_id}: {step.description}")
        
        # Check dependencies
        if not self._dependencies_met(step):
            logger.warning(f"Step {step.step_id} dependencies not met, skipping")
            result = StepResult(
                step_id=step.step_id,
                step_type=step.step_type,
                status="skipped",
                output="",
                error="Dependencies not met"
            )
            self.step_results[step.step_id] = result
            return result
        
        step_start = time.time()
        
        try:
            # Execute based on step type
            if step.step_type == StepType.REASONING:
                output = self._execute_reasoning(step)
            
            elif step.step_type == StepType.WEB_SEARCH:
                output = self._execute_web_search(step)
            
            elif step.step_type == StepType.NEWS_SEARCH:
                output = self._execute_news_search(step)
            
            elif step.step_type == StepType.KB_QUERY:
                output = self._execute_kb_query(step)
            
            elif step.step_type == StepType.AGGREGATE:
                output = self._execute_aggregate(step)
            
            elif step.step_type == StepType.COMPARE:
                output = self._execute_compare(step)
            
            else:
                output = f"Unknown step type: {step.step_type}"
            
            execution_time = time.time() - step_start
            
            result = StepResult(
                step_id=step.step_id,
                step_type=step.step_type,
                status="success",
                output=output,
                execution_time=execution_time
            )
            
            # Store result and output
            self.step_results[step.step_id] = result
            self.step_outputs[step.step_id] = output
            
            logger.info(f"Step {step.step_id} completed in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Step {step.step_id} failed: {str(e)}")
            
            execution_time = time.time() - step_start
            
            result = StepResult(
                step_id=step.step_id,
                step_type=step.step_type,
                status="failed",
                output="",
                error=str(e),
                execution_time=execution_time
            )
            
            self.step_results[step.step_id] = result
            return result
    
    def _dependencies_met(self, step: ExecutionStep) -> bool:
        """Check if step dependencies are met."""
        for dep_id in step.dependencies:
            if dep_id not in self.step_results:
                return False
            if self.step_results[dep_id].status != "success":
                return False
        return True
    
    def _execute_reasoning(self, step: ExecutionStep) -> str:
        """Execute reasoning step (LLM thinking)."""
        # Use research agent for reasoning (no tools needed)
        prompt = f"Please reason about: {step.action}"
        response = self.research_agent(prompt)
        return str(response)
    
    def _execute_web_search(self, step: ExecutionStep) -> str:
        """Execute web search step."""
        response = self.research_agent(step.action)
        return str(response)
    
    def _execute_news_search(self, step: ExecutionStep) -> str:
        """Execute news search step."""
        prompt = f"Search recent news about: {step.action}"
        response = self.research_agent(prompt)
        return str(response)
    
    def _execute_kb_query(self, step: ExecutionStep) -> str:
        """Execute knowledge base query."""
        response = self.esg_agent(step.action)
        return str(response)
    
    def _execute_aggregate(self, step: ExecutionStep) -> str:
        """Execute data aggregation step."""
        # Collect outputs from dependency steps
        dependent_data = []
        for dep_id in step.dependencies:
            if dep_id in self.step_outputs:
                dependent_data.append({
                    'step_id': dep_id,
                    'data': self.step_outputs[dep_id]
                })
        
        # Format for aggregator
        data_text = f"Aggregate the following data:\n\n"
        for item in dependent_data:
            data_text += f"Step {item['step_id']} output:\n{item['data']}\n\n"
        
        response = self.aggregator_agent(data_text)
        return str(response)
    
    def _execute_compare(self, step: ExecutionStep) -> str:
        """Execute comparison step."""
        # Collect outputs from dependency steps
        dependent_data = []
        for dep_id in step.dependencies:
            if dep_id in self.step_outputs:
                dependent_data.append({
                    'step_id': dep_id,
                    'data': self.step_outputs[dep_id]
                })
        
        # Format for comparison
        comparison_prompt = f"Compare the following data:\n\n"
        comparison_prompt += f"Comparison task: {step.action}\n\n"
        
        for item in dependent_data:
            comparison_prompt += f"Data from step {item['step_id']}:\n{item['data']}\n\n"
        
        response = self.aggregator_agent(comparison_prompt)
        return str(response)
    
    def _generate_final_answer(self, plan: ExecutionPlan) -> str:
        """
        Generate final answer from all step results.
        
        Args:
            plan: Original execution plan
        
        Returns:
            Final answer string
        """
        # Get the last step's output as the final answer
        if self.step_outputs:
            last_step_id = max(self.step_outputs.keys())
            final_answer = self.step_outputs[last_step_id]
        else:
            final_answer = "No results available"
        
        return final_answer


# Global executor instance
_executor = None


def get_executor() -> Executor:
    """Get or create executor instance."""
    global _executor
    if _executor is None:
        _executor = Executor()
    return _executor


def execute_plan(plan: ExecutionPlan) -> ExecutionResult:
    """
    Execute a plan using the global executor.
    
    Args:
        plan: ExecutionPlan to execute
    
    Returns:
        ExecutionResult
    """
    executor = get_executor()
    return executor.execute_plan(plan)


__all__ = [
    'Executor',
    'get_executor',
    'execute_plan',
    'AGGREGATOR_SYSTEM_PROMPT'
]
