"""
평가 서비스 (LangGraph 통합)
"""

import os
import json
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path
from dotenv import load_dotenv
import asyncio
from ai.agents.graph.evaluation import create_evaluation_graph
from services.storage.s3_service import S3Service
from sqlalchemy.orm import Session
from db.database import SessionLocal
from models.evaluation import Evaluation
from models.interview import Applicant, Company, InterviewSession, InterviewStatus
from models.job import Job

env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

from ai.prompts.competency_agents.common_competencies.problem_solving_prompt import create_problem_solving_evaluation_prompt
from ai.prompts.competency_agents.common_competencies.organizational_fit_prompt import create_organizational_fit_evaluation_prompt
from ai.prompts.competency_agents.common_competencies.growth_potential_prompt import create_growth_potential_evaluation_prompt
from ai.prompts.competency_agents.common_competencies.interpersonal_skill_prompt import create_interpersonal_skill_evaluation_prompt  # ⚠️ "skill" (단수)
from ai.prompts.competency_agents.common_competencies.achievement_motivation_prompt import create_achievement_motivation_evaluation_prompt

from ai.prompts.competency_agents.job_competencies.customer_journey_marketing_prompt import create_customer_journey_marketing_evaluation_prompt
from ai.prompts.competency_agents.job_competencies.data_analysis_prompt import create_md_data_analysis_evaluation_prompt
from ai.prompts.competency_agents.job_competencies.seasonal_strategy_kpi_prompt import create_seasonal_strategy_kpi_evaluation_prompt
from ai.prompts.competency_agents.job_competencies.stakeholder_collaboration_prompt import create_stakeholder_collaboration_evaluation_prompt
from ai.prompts.competency_agents.job_competencies.value_chain_optimization_prompt import create_value_chain_optimization_evaluation_prompt

from openai import AsyncOpenAI

PROMPT_GENERATORS = {
    # Common Competencies (5개)
    "problem_solving": create_problem_solving_evaluation_prompt,
    "organizational_fit": create_organizational_fit_evaluation_prompt,
    "growth_potential": create_growth_potential_evaluation_prompt,
    "interpersonal_skill": create_interpersonal_skill_evaluation_prompt, 
    "achievement_motivation": create_achievement_motivation_evaluation_prompt,
    
    # Job Competencies (5개)
    "customer_journey_marketing": create_customer_journey_marketing_evaluation_prompt,
    "md_data_analysis": create_md_data_analysis_evaluation_prompt,
    "seasonal_strategy_kpi": create_seasonal_strategy_kpi_evaluation_prompt,
    "stakeholder_collaboration": create_stakeholder_collaboration_evaluation_prompt,
    "value_chain_optimization": create_value_chain_optimization_evaluation_prompt,
}


class EvaluationService:
    """평가 서비스"""
    
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        
        from core.config import S3_BUCKET_NAME, AWS_REGION
        self.openai_client = AsyncOpenAI(api_key=api_key)
        self.graph = create_evaluation_graph()
        self.s3_service = S3Service(bucket_name=S3_BUCKET_NAME, region_name=AWS_REGION)
    
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
        competency_weights: Dict[str, float], 
        resume_data: Optional[Dict] = None 
    ) -> Dict:
        """
        면접 평가 실행
        
        Args:
            interview_id: 면접 ID
            applicant_id: 지원자 ID
            job_id: JD ID
            transcript: 면접 Transcript JSON
            competency_weights: 10개 역량 가중치
                {
                    "achievement_motivation": 0.12,
                    "growth_potential": 0.10,
                    ...
                }
            resume_data: 파싱된 Resume JSON (선택적)
        
        Returns:
            평가 결과
        """
        
        transcript_content = transcript
        transcript_s3_url = f"s3://{self.s3_service.bucket_name}/transcripts/{interview_id}_mock.json"  # 임시 S3 URL
        prompts = self._load_prompts(transcript_content)

       
        # Initial State 구성
        initial_state = {
            # 기본 정보
            "interview_id": interview_id,
            "applicant_id": applicant_id,
            "job_id": job_id,
            "transcript_s3_url": transcript_s3_url,
            "transcript_content": transcript_content,
            "transcript": transcript_content,
            "resume_data": resume_data, 
            "openai_client": self.openai_client,
            "prompts": prompts,
            
            # 가중치 
            "competency_weights": competency_weights,
            
            # Stage 1 결과 (초기화)
            "achievement_motivation_result": None,
            "growth_potential_result": None,
            "interpersonal_skill_result": None, 
            "organizational_fit_result": None,
            "problem_solving_result": None,
            "customer_journey_marketing_result": None, 
            "md_data_analysis_result": None, 
            "seasonal_strategy_kpi_result": None, 
            "stakeholder_collaboration_result": None, 
            "value_chain_optimization_result": None, 
            
            # Stage 2 결과 (초기화)
            "segment_evaluations_with_resume": [],
            "confidence_v2_calculated": False,
            "segment_overlap_adjustments": [],
            "cross_competency_flags": [],
            "aggregated_competencies": {},
            "low_confidence_list": [],
            "requires_collaboration": False,
            
            # Stage 3 결과 (초기화)
            "collaboration_results": [],
            "collaboration_count": 0,
            
            # Final 결과 (초기화)
            "final_score": None,
            "avg_confidence": None,
            "final_reliability": None,
            "reliability_note": None,
            "final_result": None,
            
            # 메타 정보
            "started_at": datetime.now(),
            "completed_at": None,
            "errors": [],
            "execution_logs": []
        }
        
       
        # 그래프 실행
        print("\n" + "="*80)
        print(f"평가 시작: Interview ID {interview_id}")
        print("="*80)
        
        result = await self.graph.ainvoke(initial_state)
        
       
        # 1. Save execution logs to S3
        execution_logs_s3_key = f"logs/evaluations/{applicant_id}/{interview_id}/{datetime.now().isoformat()}_execution_logs.json"
        agent_logs_s3_url = self.s3_service.upload_json(
            execution_logs_s3_key, result["execution_logs"]
        )

       
        # 2. Save evaluation results to DB
        db = SessionLocal()
        try:
            evaluation_record = await asyncio.to_thread(
                self._save_evaluation_to_db, 
                db, 
                result, 
                transcript_s3_url, 
                agent_logs_s3_url
            )
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
            
            # 디버깅/관찰용 상세 정보 (요청 시 출력)
            "execution_logs": result.get("execution_logs", []),
            "segment_evaluations_with_resume": result.get("segment_evaluations_with_resume", []),
            "segment_overlap_adjustments": result.get("segment_overlap_adjustments", []),
            "cross_competency_flags": result.get("cross_competency_flags", []),
            "aggregated_competencies": result.get("aggregated_competencies", {}),
            
            # 최종 점수
            "final_score": result.get("final_score"),
            "avg_confidence": result.get("avg_confidence"),
            "final_reliability": result.get("final_reliability"),
            "reliability_note": result.get("reliability_note"),
            
            # 역량별 상세
            "competency_details": result.get("final_result", {}).get("competency_details", {}),
            
            # Low Confidence 요약
            "low_confidence_summary": result.get("final_result", {}).get("low_confidence_summary", {}),
            
            # Collaboration 요약
            "collaboration_summary": result.get("final_result", {}).get("collaboration_summary", {}),
            
            # 메타 정보
            "started_at": result["started_at"].isoformat(),
            "completed_at": datetime.now().isoformat()
        }

    def _save_evaluation_to_db(
        self, 
        db: Session, 
        state: Dict, 
        transcript_s3_url: str, 
        agent_logs_s3_url: str
    ):
        """
        평가 결과를 DB에 저장
        """
       
        # FK가 없는 경우 테스트 편의를 위해 최소 엔터티를 생성
        applicant_id = state["applicant_id"]
        job_id = state["job_id"]

        applicant = db.query(Applicant).filter(Applicant.id == applicant_id).first()
        if not applicant:
            applicant = Applicant(
                id=applicant_id,
                name=f"Applicant {applicant_id}",
                email=f"applicant{applicant_id}@example.com"
            )
            db.add(applicant)

        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            # 회사도 없을 수 있으므로 기본 Company 생성
            company = db.query(Company).filter(Company.id == 1).first()
            if not company:
                company = Company(id=1, name="Default Company")
                db.add(company)
            job = Job(
                id=job_id,
                company_id=company.id,
                title=f"Job {job_id}",
                description="Placeholder job for testing"
            )
            db.add(job)

        # 인터뷰 세션이 없으면 생성 (FK 보호)
        interview_id = state.get("interview_id")
        if interview_id:
            interview = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
            if not interview:
                interview = InterviewSession(
                    id=interview_id,
                    applicant_id=applicant_id,
                    company_id=job.company_id,
                    status=InterviewStatus.COMPLETED
                )
                db.add(interview)

        # FK 객체들을 먼저 flush해서 PK를 확정
        db.flush()

       
        # 1. 역량 평가 결과(증거)를 S3에 업로드
       
        aggregated_competencies = state.get("aggregated_competencies", {})
        
        evidence_s3_key = f"evaluations/{state['interview_id']}/evidence.json"
        evidence_s3_url = self.s3_service.upload_json(evidence_s3_key, aggregated_competencies)

       
        # 2. Evaluation 레코드 생성
       
        final_result = state.get("final_result", {})
        
        evaluation_record = Evaluation(
            applicant_id=state["applicant_id"],
            job_id=state["job_id"],
            interview_id=state["interview_id"],
            evaluation_status="completed",
            
            # Scores (최종 점수)
            match_score=state.get("final_score", 0.0),
            normalized_score=state.get("final_score", 0.0),
            weighted_score=state.get("final_score", 0.0),
            confidence_score=state.get("avg_confidence", 0.0),

            # S3 URL
            transcript_s3_url=transcript_s3_url,
            agent_logs_s3_url=agent_logs_s3_url,
            evidence_s3_url=evidence_s3_url,

            # 역량별 점수 (수정됨! - 역량 이름 변경)
            problem_solving=aggregated_competencies.get("problem_solving", {}).get("overall_score", 0),
            organizational_fit=aggregated_competencies.get("organizational_fit", {}).get("overall_score", 0),
            growth_potential=aggregated_competencies.get("growth_potential", {}).get("overall_score", 0),
            interpersonal_skills=aggregated_competencies.get("interpersonal_skill", {}).get("overall_score", 0),  # ⚠️ "skill" → DB는 "skills"
            achievement_motivation=aggregated_competencies.get("achievement_motivation", {}).get("overall_score", 0),
            
            # Job Competencies - 수정 필요! (DB 스키마에 컬럼 추가 필요)
            # 임시로 기존 컬럼 재사용
            structured_thinking=aggregated_competencies.get("customer_journey_marketing", {}).get("overall_score", 0),
            business_documentation=aggregated_competencies.get("md_data_analysis", {}).get("overall_score", 0),
            financial_literacy=aggregated_competencies.get("seasonal_strategy_kpi", {}).get("overall_score", 0),
            industry_learning=aggregated_competencies.get("stakeholder_collaboration", {}).get("overall_score", 0),
            stakeholder_management=aggregated_competencies.get("value_chain_optimization", {}).get("overall_score", 0),

            # Aggregation 결과 (삭제됨!)
            job_aggregation=None,  # Job/Common 구분 제거
            common_aggregation=None,  # Job/Common 구분 제거
            
            # Validation 결과
            validation_result={
                "low_confidence_list": state.get("low_confidence_list", []),
                "cross_competency_flags": state.get("cross_competency_flags", []),
            },

            # JSON 필드
            competency_scores={
                comp_name: comp_data.get("overall_score", 0)
                for comp_name, comp_data in aggregated_competencies.items()
            },
            individual_evaluations=aggregated_competencies,
            aggregated_evaluation=final_result,
            match_result={
                "final_score": state.get("final_score"),
                "reliability": state.get("final_reliability"),
                "reliability_note": state.get("reliability_note")
            },
            reasoning_log={},
            rubric_scores={},
            normalization_metadata={},
            evaluation_metadata={
                "resume_verified_count": sum(
                    comp.get("resume_verified_count", 0)
                    for comp in aggregated_competencies.values()
                ),
                "segment_overlap_adjustments": len(state.get("segment_overlap_adjustments", [])),
                "collaboration_count": state.get("collaboration_count", 0)
            },
            
            created_at=state["started_at"],
            updated_at=datetime.now()
        )
        db.add(evaluation_record)
        db.commit()
        db.refresh(evaluation_record)
        return evaluation_record
