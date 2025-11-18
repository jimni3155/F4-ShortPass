# ai/agents/evaluator_nodes.py
"""
6개 역량 평가 노드
각 노드는 독립적으로 실행 가능하며 병렬 처리됨
"""

import asyncio
import json
from typing import Dict, Any
from datetime import datetime

from ai.utils.llm_client import LLMClient
from ai.agents.state import EvaluationState
from ai.prompts.evaluation_agents.job_expertise_prompt import JOB_EXPERTISE_PROMPT
from ai.prompts.evaluation_agents.analytical_prompt import ANALYTICAL_PROMPT
from ai.prompts.evaluation_agents.execution_prompt import EXECUTION_PROMPT
from ai.prompts.evaluation_agents.relationship_prompt import RELATIONSHIP_PROMPT
from ai.prompts.evaluation_agents.resilience_prompt import RESILIENCE_PROMPT
from ai.prompts.evaluation_agents.influence_prompt import INFLUENCE_PROMPT


class EvaluatorNodes:
    """
    6개 역량 평가 노드 정의
    """
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
    
    async def _execute_evaluation(
        self,
        node_name: str,
        prompt_template: str,
        state: EvaluationState,
        additional_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        공통 평가 실행 로직
        
        Args:
            node_name: 노드 이름 (로깅용)
            prompt_template: 평가 프롬프트 템플릿
            state: 현재 상태
            additional_context: 추가 컨텍스트 (Job Expertise용)
        
        Returns:
            평가 결과 dict
        """
        start_time = datetime.now()
        
        try:
            # 프롬프트 변수 준비
            context = {
                "transcript": state["interview_transcript"],
                "applicant_skills": ", ".join(state["applicant_skills"]),
                "applicant_experience_years": state["applicant_experience_years"],
                "standards": state["evaluation_standards"],
            }
            
            # 추가 컨텍스트 병합 (Job Expertise용)
            if additional_context:
                context.update(additional_context)
            
            # 프롬프트 생성
            prompt = prompt_template.format(**context)
            
            # LLM 호출
            response = await self.llm_client.ainvoke(prompt)
            
            # JSON 파싱
            response_text = response.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            result = json.loads(response_text)
            
            # 실행 시간 기록
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "result": result,
                "execution_time": execution_time,
                "error": None
            }
            
        except json.JSONDecodeError as e:
            return {
                "result": None,
                "execution_time": (datetime.now() - start_time).total_seconds(),
                "error": f"JSON parsing error: {str(e)}"
            }
        except Exception as e:
            return {
                "result": None,
                "execution_time": (datetime.now() - start_time).total_seconds(),
                "error": f"Evaluation error: {str(e)}"
            }
    
    # ==================== 6개 Evaluator Nodes ====================
    
    async def job_expertise_evaluator(self, state: EvaluationState) -> Dict[str, Any]:
        """
        Job Expertise 역량 평가
        동적 프롬프트 생성 (JD 기반)
        """
        additional_context = {
            "job_description": state["job_description"],
            "job_title": state["job_title"],
            "required_skills": ", ".join(state["required_skills"]),
            "preferred_skills": ", ".join(state["preferred_skills"]),
            "domain_requirements": ", ".join(state["domain_requirements"]),
            "dynamic_evaluation_criteria": ", ".join(state["dynamic_evaluation_criteria"]),
            "applicant_portfolio": json.dumps(state["applicant_portfolio"], ensure_ascii=False),
            "applicant_resume": json.dumps(state["applicant_resume"], ensure_ascii=False),
        }
        
        eval_result = await self._execute_evaluation(
            node_name="job_expertise_evaluator",
            prompt_template=JOB_EXPERTISE_PROMPT,
            state=state,
            additional_context=additional_context
        )
        
        return {
            "job_expertise_result": eval_result["result"],
            "execution_logs": [
                {
                    "node": "job_expertise_evaluator",
                    "execution_time": eval_result["execution_time"],
                    "error": eval_result["error"],
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
    
    async def analytical_evaluator(self, state: EvaluationState) -> Dict[str, Any]:
        """
        Analytical (분석적 사고) 역량 평가
        """
        eval_result = await self._execute_evaluation(
            node_name="analytical_evaluator",
            prompt_template=ANALYTICAL_PROMPT,
            state=state
        )
        
        return {
            "analytical_result": eval_result["result"],
            "execution_logs": [
                {
                    "node": "analytical_evaluator",
                    "execution_time": eval_result["execution_time"],
                    "error": eval_result["error"],
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
    
    async def execution_evaluator(self, state: EvaluationState) -> Dict[str, Any]:
        """
        Execution (실행력) 역량 평가
        """
        additional_context = {
            "applicant_portfolio_summary": json.dumps(
                state["applicant_portfolio"], 
                ensure_ascii=False
            ),
        }
        
        eval_result = await self._execute_evaluation(
            node_name="execution_evaluator",
            prompt_template=EXECUTION_PROMPT,
            state=state,
            additional_context=additional_context
        )
        
        return {
            "execution_result": eval_result["result"],
            "execution_logs": [
                {
                    "node": "execution_evaluator",
                    "execution_time": eval_result["execution_time"],
                    "error": eval_result["error"],
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
    
    async def relationship_evaluator(self, state: EvaluationState) -> Dict[str, Any]:
        """
        Relationship (관계 형성) 역량 평가
        """
        eval_result = await self._execute_evaluation(
            node_name="relationship_evaluator",
            prompt_template=RELATIONSHIP_PROMPT,
            state=state
        )
        
        return {
            "relationship_result": eval_result["result"],
            "execution_logs": [
                {
                    "node": "relationship_evaluator",
                    "execution_time": eval_result["execution_time"],
                    "error": eval_result["error"],
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
    
    async def resilience_evaluator(self, state: EvaluationState) -> Dict[str, Any]:
        """
        Resilience (회복탄력성) 역량 평가
        """
        additional_context = {
            "applicant_resume_summary": json.dumps(
                state["applicant_resume"], 
                ensure_ascii=False
            ),
        }
        
        eval_result = await self._execute_evaluation(
            node_name="resilience_evaluator",
            prompt_template=RESILIENCE_PROMPT,
            state=state,
            additional_context=additional_context
        )
        
        return {
            "resilience_result": eval_result["result"],
            "execution_logs": [
                {
                    "node": "resilience_evaluator",
                    "execution_time": eval_result["execution_time"],
                    "error": eval_result["error"],
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
    
    async def influence_evaluator(self, state: EvaluationState) -> Dict[str, Any]:
        """
        Influence (영향력) 역량 평가
        """
        additional_context = {
            "applicant_portfolio_summary": json.dumps(
                state["applicant_portfolio"], 
                ensure_ascii=False
            ),
        }
        
        eval_result = await self._execute_evaluation(
            node_name="influence_evaluator",
            prompt_template=INFLUENCE_PROMPT,
            state=state,
            additional_context=additional_context
        )
        
        return {
            "influence_result": eval_result["result"],
            "execution_logs": [
                {
                    "node": "influence_evaluator",
                    "execution_time": eval_result["execution_time"],
                    "error": eval_result["error"],
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }