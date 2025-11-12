"""
LangGraph-based Multi-Agent Evaluation System
Orchestrates 6 competency evaluators in parallel for efficient candidate assessment.
"""

import asyncio
import json
from typing import TypedDict, Annotated, Literal, Optional
from datetime import datetime
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from ai.prompts.agents.router_prompt import ROUTER_PROMPT
from ai.prompts.agents.aggregator_prompt import AGGREGATOR_PROMPT
from ai.prompts.agents.matcher_prompt import MATCHER_PROMPT
from ai.prompts.scorer_agents.evaluator_job_expertise_prompt import JOB_EXPERTISE_PROMPT
from ai.prompts.scorer_agents.evaluator_problem_solving__prompt import PROBLEM_SOLVING_PROMPT 
from ai.prompts.scorer_agents.evaluator_organizational_fit_prompt import ORGANIZATIONAL_FIT_PROMPT
from ai.prompts.scorer_agents.evaluator_growth_potential_prompt import GROWTH_POTENTIAL_PROMPT
from ai.prompts.scorer_agents.evaluator_interpersonal_skill_prompt import INTERPERSONAL_SKILL_PROMPT
from ai.prompts.scorer_agents.evaluator_achievement_motivation_prompt import ACHIEVEMENT_MOTIVATION_PROMPT

# Import LLM client
from ai.utils.llm_client import LLMClient


# ============================================================================
# State Definition
# ============================================================================

class EvaluationState(TypedDict):
    """State shared across all agents in the evaluation workflow."""
    
    # Input data
    interview_transcript: str
    resume: str
    job_description: dict
    category_weights: dict  # Company-specific competency weights from JD
    position_type: str
    
    # Router output
    active_agents: list[str]
    priority_order: list[str]
    context_summary: str
    
    # Evaluator outputs (6 competencies)
    job_expertise_result: Optional[dict] 
    problem_solving_result: Optional[dict] 
    organizational_fit_result: Optional[dict] 
    growth_potential_result: Optional[dict] 
    interpersonal_skill_result: Optional[dict] 
    achievement_motivation_result: Optional[dict] 
    
    # Aggregated evaluation
    aggregated_evaluation: Optional[dict] 
    
    # Final matching result
    match_result: Optional[dict] 
    
    # Metadata
    errors: list[str]
    timestamp: str


# ============================================================================
# Agent Implementations
# ============================================================================

class MultiAgentEvaluator:
    """Main orchestrator for multi-agent evaluation system."""
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Construct the LangGraph workflow."""
        workflow = StateGraph(EvaluationState)
        
        # Add nodes
        workflow.add_node("router", self._router_agent)
        workflow.add_node("job_expertise_evaluator", self._job_expertise_agent)
        workflow.add_node("problem_solving_evaluator", self._problem_solving_agent)
        workflow.add_node("organizational_fit_evaluator", self._organizational_fit_agent)
        workflow.add_node("growth_potential_evaluator", self._growth_potential_agent)
        workflow.add_node("interpersonal_skill_evaluator", self._interpersonal_skill_agent)
        workflow.add_node("achievement_motivation_evaluator", self._achievement_motivation_agent)
        workflow.add_node("aggregator", self._aggregator_agent)
        workflow.add_node("matcher", self._matcher_agent)
        
        # Define workflow edges
        workflow.set_entry_point("router")
        
        # Router fans out to all 6 evaluators (parallel execution)
        workflow.add_edge("router", "job_expertise_evaluator")
        workflow.add_edge("router", "problem_solving_evaluator")
        workflow.add_edge("router", "organizational_fit_evaluator")
        workflow.add_edge("router", "growth_potential_evaluator")
        workflow.add_edge("router", "interpersonal_skill_evaluator")
        workflow.add_edge("router", "achievement_motivation_evaluator")
        
        # All evaluators converge to aggregator
        workflow.add_edge("job_expertise_evaluator", "aggregator")
        workflow.add_edge("problem_solving_evaluator", "aggregator")
        workflow.add_edge("organizational_fit_evaluator", "aggregator")
        workflow.add_edge("growth_potential_evaluator", "aggregator")
        workflow.add_edge("interpersonal_skill_evaluator", "aggregator")
        workflow.add_edge("achievement_motivation_evaluator", "aggregator")
        
        # Aggregator → Matcher → End
        workflow.add_edge("aggregator", "matcher")
        workflow.add_edge("matcher", END)
        
        return workflow.compile()
    
    # ------------------------------------------------------------------------
    # Router Agent
    # ------------------------------------------------------------------------
    
    async def _router_agent(self, state: EvaluationState) -> dict:
        """
        Analyzes input and determines evaluation strategy.
        Currently activates all 6 agents but sets priority order.
        """
        try:
            prompt = ROUTER_PROMPT.format(
                job_description=json.dumps(state["job_description"], indent=2),
                position_type=state["position_type"]
            )
            
            response = await self.llm_client.generate(
                prompt=prompt,
                response_format={"type": "json_schema"},
                temperature=0.2
            )
            
            router_output = self._parse_json_response(response)
            
            return {
                "active_agents": router_output.get("active_agents", [
                    "job_expertise", "problem_solving", "organizational_fit",
                    "growth_potential", "interpersonal_skill", "achievement_motivation"
                ]),
                "priority_order": router_output.get("priority_order", []),
                "context_summary": router_output.get("context_summary", ""),
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            return {
                "active_agents": [],
                "priority_order": [],
                "context_summary": "",
                "errors": state.get("errors", []) + [f"Router error: {str(e)}"]
            }
    
    # ------------------------------------------------------------------------
    # Evaluator Agents (6 competencies)
    # ------------------------------------------------------------------------
    
    async def _job_expertise_agent(self, state: EvaluationState) -> dict:
        """Evaluates job-specific technical competencies."""
        return await self._run_evaluator(
            state=state,
            competency="job_expertise",
            prompt_template=JOB_EXPERTISE_PROMPT,
            result_key="job_expertise_result"
        )
    
    async def _problem_solving_agent(self, state: EvaluationState) -> dict:
        """Evaluates problem-solving capabilities."""
        return await self._run_evaluator(
            state=state,
            competency="problem_solving",
            prompt_template=PROBLEM_SOLVING_PROMPT,
            result_key="problem_solving_result"
        )
    
    async def _organizational_fit_agent(self, state: EvaluationState) -> dict:
        """Evaluates organizational culture fit."""
        return await self._run_evaluator(
            state=state,
            competency="organizational_fit",
            prompt_template=ORGANIZATIONAL_FIT_PROMPT,
            result_key="organizational_fit_result"
        )
    
    async def _growth_potential_agent(self, state: EvaluationState) -> dict:
        """Evaluates candidate's growth potential."""
        return await self._run_evaluator(
            state=state,
            competency="growth_potential",
            prompt_template=GROWTH_POTENTIAL_PROMPT,
            result_key="growth_potential_result"
        )
    
    async def _interpersonal_skill_agent(self, state: EvaluationState) -> dict:
        """Evaluates interpersonal and collaboration skills."""
        return await self._run_evaluator(
            state=state,
            competency="interpersonal_skill",
            prompt_template=INTERPERSONAL_SKILL_PROMPT,
            result_key="interpersonal_skill_result"
        )
    
    async def _achievement_motivation_agent(self, state: EvaluationState) -> dict:
        """Evaluates achievement motivation and drive."""
        return await self._run_evaluator(
            state=state,
            competency="achievement_motivation",
            prompt_template=ACHIEVEMENT_MOTIVATION_PROMPT,
            result_key="achievement_motivation_result"
        )
    
    async def _run_evaluator(
        self,
        state: EvaluationState,
        competency: str,
        prompt_template: str,
        result_key: str
    ) -> dict:
        """
        Generic evaluator runner for all 6 competencies.
        Handles prompt formatting, LLM invocation, and error handling.
        """
        try:
            # Get competency-specific weight
            competency_weight = state["category_weights"].get(competency, 0)
            
            # Format prompt with state data
            prompt = prompt_template.format(
                interview_transcript=state["interview_transcript"],
                resume=state["resume"],
                job_description=json.dumps(state["job_description"], indent=2),
                category_weight=competency_weight,
                position_type=state["position_type"]
            )
            
            # Invoke LLM
            response = await self.llm_client.generate(
                prompt=prompt,
                response_format={"type": "json_schema"},
                temperature=0.3
            )
            
            # Parse and validate response
            evaluation_result = self._parse_json_response(response)
            evaluation_result["competency"] = competency
            evaluation_result["weight"] = competency_weight
            
            return {result_key: evaluation_result}
        
        except Exception as e:
            error_msg = f"{competency} evaluator error: {str(e)}"
            return {
                result_key: {
                    "competency": competency,
                    "error": error_msg,
                    "overall_score": 0,
                    "confidence": 0.0
                },
                "errors": state.get("errors", []) + [error_msg]
            }
    
    # ------------------------------------------------------------------------
    # Aggregator Agent
    # ------------------------------------------------------------------------
    
    async def _aggregator_agent(self, state: EvaluationState) -> dict:
        """
        Aggregates all 6 competency evaluations into a comprehensive assessment.
        Waits for all evaluators to complete (LangGraph handles synchronization).
        """
        try:
            # Collect all evaluation results
            evaluations = {
                "job_expertise": state.get("job_expertise_result"),
                "problem_solving": state.get("problem_solving_result"),
                "organizational_fit": state.get("organizational_fit_result"),
                "growth_potential": state.get("growth_potential_result"),
                "interpersonal_skill": state.get("interpersonal_skill_result"),
                "achievement_motivation": state.get("achievement_motivation_result")
            }
            
            # Filter out None values (shouldn't happen but safety check)
            evaluations = {k: v for k, v in evaluations.items() if v is not None}
            
            # Prepare aggregation prompt
            prompt = AGGREGATOR_PROMPT.format(
                evaluations=json.dumps(evaluations, indent=2),
                category_weights=json.dumps(state["category_weights"], indent=2),
                position_type=state["position_type"]
            )
            
            # Invoke LLM for synthesis
            response = await self.llm_client.generate(
                prompt=prompt,
                response_format={"type": "json_schema"},
                temperature=0.2
            )
            
            aggregated_result = self._parse_json_response(response)
            
            return {"aggregated_evaluation": aggregated_result}
        
        except Exception as e:
            error_msg = f"Aggregator error: {str(e)}"
            return {
                "aggregated_evaluation": {
                    "error": error_msg,
                    "weighted_score": 0,
                    "confidence_score": 0.0
                },
                "errors": state.get("errors", []) + [error_msg]
            }
    
    # ------------------------------------------------------------------------
    # Matcher Agent
    # ------------------------------------------------------------------------
    
    async def _matcher_agent(self, state: EvaluationState) -> dict:
        """
        Determines candidate-job match quality and provides hiring recommendation.
        """
        try:
            prompt = MATCHER_PROMPT.format(
                aggregated_evaluation=json.dumps(state["aggregated_evaluation"], indent=2),
                job_description=json.dumps(state["job_description"], indent=2),
                category_weights=json.dumps(state["category_weights"], indent=2),
                position_type=state["position_type"]
            )
            
            response = await self.llm_client.generate(
                prompt=prompt,
                response_format={"type": "json_schema"},
                temperature=0.1  # Lower temp for consistent matching decisions
            )
            
            match_result = self._parse_json_response(response)
            match_result["timestamp"] = datetime.utcnow().isoformat()
            
            return {"match_result": match_result}
        
        except Exception as e:
            error_msg = f"Matcher error: {str(e)}"
            return {
                "match_result": {
                    "error": error_msg,
                    "match_score": 0,
                    "recommendation": {"decision": "error"}
                },
                "errors": state.get("errors", []) + [error_msg]
            }
    
    # ------------------------------------------------------------------------
    # Utility Methods
    # ------------------------------------------------------------------------
    
    def _parse_json_response(self, response: dict) -> dict:
        """
        Safely parse JSON from LLM response.
        Handles both direct JSON and text-wrapped JSON.
        """
        if isinstance(response, dict):
            # If response_format was json_schema, should already be dict
            if "text" in response:
                # Try to parse text as JSON
                try:
                    return json.loads(response["text"])
                except json.JSONDecodeError:
                    return response
            return response
        
        # Fallback
        return {"error": "Invalid response format", "raw_response": str(response)}
    
    # ------------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------------
    
    async def evaluate(
        self,
        interview_transcript: str,
        resume: str,
        job_description: dict,
        category_weights: dict,
        position_type: str
    ) -> dict:
        """
        Main entry point for candidate evaluation.
        
        Args:
            interview_transcript: Full transcript of the interview
            resume: Candidate's resume text
            job_description: JD as dict with required fields
            category_weights: Company-specific competency weights (from JD extraction)
            position_type: Position classification (e.g., "기술 중심", "협업 중심")
        
        Returns:
            Complete evaluation result including match_result
        """
        initial_state: EvaluationState = {
            "interview_transcript": interview_transcript,
            "resume": resume,
            "job_description": job_description,
            "category_weights": category_weights,
            "position_type": position_type,
            
            # Initialize empty results
            "active_agents": [],
            "priority_order": [],
            "context_summary": "",
            
            "job_expertise_result": None,
            "problem_solving_result": None,
            "organizational_fit_result": None,
            "growth_potential_result": None,
            "interpersonal_skill_result": None,
            "achievement_motivation_result": None,
            
            "aggregated_evaluation": None,
            "match_result": None,
            
            "errors": [],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Run workflow
        final_state = await self.workflow.ainvoke(initial_state)
        
        return {
            "match_result": final_state.get("match_result"),
            "aggregated_evaluation": final_state.get("aggregated_evaluation"),
            "individual_evaluations": {
                "job_expertise": final_state.get("job_expertise_result"),
                "problem_solving": final_state.get("problem_solving_result"),
                "organizational_fit": final_state.get("organizational_fit_result"),
                "growth_potential": final_state.get("growth_potential_result"),
                "interpersonal_skill": final_state.get("interpersonal_skill_result"),
                "achievement_motivation": final_state.get("achievement_motivation_result")
            },
            "metadata": {
                "timestamp": final_state.get("timestamp"),
                "errors": final_state.get("errors", []),
                "position_type": position_type
            }
        }