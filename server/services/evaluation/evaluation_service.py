"""
평가 서비스 (LangGraph 통합)
"""

import os
import json
from datetime import datetime
from typing import Dict
from pathlib import Path
from dotenv import load_dotenv
import asyncio # Add this
from ai.agents.graph.evaluation import create_evaluation_graph
from services.storage.s3_service_v2 import S3ServiceV2
from sqlalchemy.orm import Session # Add this
from db.database import SessionLocal # Add this
from models.evaluation import Evaluation # Add this

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
        self.s3_service = S3ServiceV2()
    
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
        transcript_s3_url: str,
        job_weights: Dict[str, float],
        common_weights: Dict[str, float],
        job_common_ratio: Dict[str, float] = None
    ) -> Dict:
        """면접 평가 실행"""

        transcript_content = await self.s3_service.get_json_file(transcript_s3_url)
        prompts = self._load_prompts(transcript_content)

        initial_state = {
            # 기본 정보
            "interview_id": interview_id,
            "applicant_id": applicant_id,
            "job_id": job_id,

            "transcript_s3_url": transcript_s3_url,
            "transcript_content": transcript_content,
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

        # 1. Save execution logs to S3
        execution_logs_s3_key = f"evaluation-logs/{applicant_id}/{interview_id}/{datetime.now().isoformat()}_execution_logs.json"
        agent_logs_s3_url = await self.s3_service.upload_json_data(
            result["execution_logs"], execution_logs_s3_key
        )

        # 2. Save evaluation results to DB
        db = SessionLocal()
        try:
            evaluation_record = await asyncio.to_thread(self._save_evaluation_to_db, 
                                                         db, 
                                                         result, 
                                                         transcript_s3_url, 
                                                         agent_logs_s3_url)
            evaluation_id = evaluation_record.id
        finally:
            await asyncio.to_thread(db.close)
        
        print("\n" + "="*80)
        print("평가 완료")
        print("="*80)
        
        # 최종 결과 구성
        return {
            "evaluation_id": evaluation_id,
            "interview_id": interview_id,
            "applicant_id": applicant_id,
            "job_id": job_id,
            "transcript_s3_url": transcript_s3_url,
            "agent_logs_s3_url": agent_logs_s3_url,

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

            "completed_at": datetime.now().isoformat()
        }

    def _save_evaluation_to_db(self, 
                                        db: Session, 
                                        state: Dict, 
                                        transcript_s3_url: str, 
                                        agent_logs_s3_url: str):
        """
        평가 결과를 DB에 저장
        """
        evaluation_record = Evaluation(
            applicant_id=state["applicant_id"],
            job_id=state["job_id"],
            interview_id=state["interview_id"],
            
            # scores (임시, 추후 보완)
            match_score=0.0, # TODO: 실제 점수 계산 로직 필요
            normalized_score=0.0,
            weighted_score=0.0,
            confidence_score=0.0,

            # S3 URL
            transcript_s3_url=transcript_s3_url,
            agent_logs_s3_url=agent_logs_s3_url,

            # LangGraph 결과
            problem_solving=state.get("problem_solving_result"),
            organizational_fit=state.get("organizational_fit_result"),
            growth_potential=state.get("growth_potential_result"),
            interpersonal_skills=state.get("interpersonal_skills_result"),
            achievement_motivation=state.get("achievement_motivation_result"),
            structured_thinking=state.get("structured_thinking_result"),
            business_documentation=state.get("business_documentation_result"),
            financial_literacy=state.get("financial_literacy_result"),
            industry_learning=state.get("industry_learning_result"),
            stakeholder_management=state.get("stakeholder_management_result"),
            job_aggregation=state.get("job_aggregation_result"),
            common_aggregation=state.get("common_aggregation_result"),
            validation_result={
                "low_confidence_competencies": state.get("low_confidence_competencies", []),
                "validation_notes": state.get("validation_notes"),
                "requires_revaluation": state.get("requires_revaluation", False),
            },

            # JSON 필드 (임시, 추후 보완)
            competency_scores={},
            individual_evaluations={},
            aggregated_evaluation={},
            match_result={},
            reasoning_log={},
            rubric_scores={},
            normalization_metadata={},
            evaluation_metadata={},
            
            created_at=state["started_at"],
            updated_at=datetime.now()
        )
        db.add(evaluation_record)
        db.commit()
        db.refresh(evaluation_record)
        return evaluation_record

