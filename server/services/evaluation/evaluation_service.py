"""
평가 서비스 (LangGraph 통합)
"""

import os
import json
from datetime import datetime
from typing import Dict
from pathlib import Path
from dotenv import load_dotenv
from ai.agents.graph.evaluation import create_evaluation_graph

# .env 파일 로드
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

# 프롬프트 생성 함수 import
from ai.prompts.competency_agents.common_competencies.problem_solving_prompt import create_problem_solving_evaluation_prompt
from ai.prompts.competency_agents.common_competencies.organizational_fit_prompt import create_organizational_fit_evaluation_prompt
from ai.prompts.competency_agents.common_competencies.growth_potential_prompt import create_growth_potential_evaluation_prompt
from ai.prompts.competency_agents.common_competencies.interpersonal_skill_prompt import create_interpersonal_skill_evaluation_prompt
from ai.prompts.competency_agents.common_competencies.achievement_motivation_prompt import create_achievement_motivation_evaluation_prompt
from ai.prompts.competency_agents.job_competencies.structured_thinking_prompt import create_structured_thinking_evaluation_prompt
from ai.prompts.competency_agents.job_competencies.business_documentation_prompt import create_business_documentation_evaluation_prompt
from ai.prompts.competency_agents.job_competencies.financing_literacy_prompt import create_financial_literacy_evaluation_prompt
from ai.prompts.competency_agents.job_competencies.industry_learning_prompt import create_industry_learning_evaluation_prompt
from ai.prompts.competency_agents.job_competencies.stakeholder_coordination_prompt import create_stakeholder_management_evaluation_prompt
from openai import AsyncOpenAI

PROMPT_GENERATORS = {
    "problem_solving": create_problem_solving_evaluation_prompt,
    "organizational_fit": create_organizational_fit_evaluation_prompt,
    "growth_potential": create_growth_potential_evaluation_prompt,
    "interpersonal_skills": create_interpersonal_skill_evaluation_prompt,
    "achievement_motivation": create_achievement_motivation_evaluation_prompt,
    "structured_thinking": create_structured_thinking_evaluation_prompt,
    "business_documentation": create_business_documentation_evaluation_prompt,
    "financial_literacy": create_financial_literacy_evaluation_prompt,
    "industry_learning": create_industry_learning_evaluation_prompt,
    "stakeholder_management": create_stakeholder_management_evaluation_prompt,
}


class EvaluationService:
    """평가 서비스"""
    
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        
        self.openai_client = AsyncOpenAI(api_key=api_key)
        self.graph = create_evaluation_graph()
    
    def _load_prompts(self, transcript: Dict) -> Dict[str, str]:
        """프롬프트 로딩"""
        transcript_str = json.dumps(transcript, ensure_ascii=False, indent=2)
        return {
            name: generator(transcript_str)
            for name, generator in PROMPT_GENERATORS.items()
        }
    
    async def evaluate_interview(
        self,
        interview_id: int,
        applicant_id: int,
        job_id: int,
        transcript: Dict,
        job_weights: Dict[str, float],
        common_weights: Dict[str, float],
        job_common_ratio: Dict[str, float] = None
    ) -> Dict:
        """면접 평가 실행"""

        if job_common_ratio is None:
            job_common_ratio = {"job": 0.6, "common": 0.4}

        prompts = self._load_prompts(transcript)
        
        initial_state = {
            # 기본 정보
            "interview_id": interview_id,
            "applicant_id": applicant_id,
            "job_id": job_id,
            "transcript": transcript,
            "openai_client": self.openai_client,
            "prompts": prompts,
            
            # 가중치
            "job_weights": job_weights,
            "common_weights": common_weights,
            "job_common_ratio": job_common_ratio,
            
            # Phase 1 결과 (초기화)
            "structured_thinking_result": None,
            "business_documentation_result": None,
            "financial_literacy_result": None,
            "industry_learning_result": None,
            "stakeholder_management_result": None,
            "problem_solving_result": None,
            "organizational_fit_result": None,
            "growth_potential_result": None,
            "interpersonal_skills_result": None,
            "achievement_motivation_result": None,
            "job_aggregation_result": None,
            "common_aggregation_result": None,
            "low_confidence_competencies": [],
            "validation_notes": None,
            "requires_revaluation": False,
            
            # Phase 2 결과 (초기화)
            "evidence_conflicts": [],
            "low_confidence_list": [],
            "requires_collaboration": False,
            
            # Phase 3 결과 (초기화)
            "mediation_results": [],
            "adversarial_results": [],
            "collaboration_count": 0,
            
            # Phase 4 결과 (초기화)
            "final_score": None,
            "avg_confidence": None,
            "final_reliability": None,
            "reliability_note": None,
            "final_result": None,
            
            # 메타 정보
            "started_at": datetime.now(),
            "completed_at": None,
            "errors": [],
            "execution_logs": [],
            "structured_transcript": None
        }
        
        # 그래프 실행
        print("\n" + "="*80)
        print(f"평가 시작: Interview ID {interview_id}")
        print("="*80)
        
        result = await self.graph.ainvoke(initial_state)
        
        print("\n" + "="*80)
        print("평가 완료")
        print("="*80)
        
        # 최종 결과 구성
        return {
            # 기본 정보
            "interview_id": interview_id,
            "applicant_id": applicant_id,
            "job_id": job_id,
            
            # Phase 1 결과
            "job_aggregation": result["job_aggregation_result"],
            "common_aggregation": result["common_aggregation_result"],
            "validation": {
                "low_confidence_competencies": result["low_confidence_competencies"],
                "validation_notes": result["validation_notes"],
                "requires_revaluation": result["requires_revaluation"]
            },
            
            # Phase 2 결과
            "issues_detected": {
                "evidence_conflicts": result.get("evidence_conflicts", []),
                "low_confidence_list": result.get("low_confidence_list", []),
                "requires_collaboration": result.get("requires_collaboration", False)
            },
            
            # Phase 3 결과 (있다면)
            "collaboration": {
                "mediation_results": result.get("mediation_results", []),
                "adversarial_results": result.get("adversarial_results", []),
                "collaboration_count": result.get("collaboration_count", 0)
            },
            
            # Phase 4 최종 결과
            "final_result": result.get("final_result", {}),
            "final_score": result.get("final_score"),
            "avg_confidence": result.get("avg_confidence"),
            "final_reliability": result.get("final_reliability"),
            "reliability_note": result.get("reliability_note"),
            
            # 메타 정보
            "started_at": result["started_at"].isoformat(),
            "completed_at": result.get("completed_at", datetime.now()).isoformat(),
            "execution_logs": result.get("execution_logs", []),
            "errors": result.get("errors", [])
        }