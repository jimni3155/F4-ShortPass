# app/services/interview_evaluation_service.py
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from schemas.interview import AnswerEvaluation
from ai.scorers.answer_scorer import AnswerScorer
from models.interview import InterviewResult, InterviewSession, Question

class InterviewEvaluationService:
    """면접 평가 및 결과 처리"""
    
    def __init__(
        self,
        db: Session,
        answer_scorer: AnswerScorer
    ):
        self.db = db
        self.answer_scorer = answer_scorer
    
    async def evaluate_answer(
        self,
        interview_id: int,
        question_id: int,
        answer_text: str,
        is_common: bool = False,
        job_id: Optional[int] = None,
        context: Dict[str, Any] = None
    ) -> AnswerEvaluation:
        """
        단일 답변 평가
        
        Args:
            interview_id: 면접 세션 ID
            question_id: 질문 ID
            answer_text: 지원자 답변
            is_common: 공통 질문 여부
            job_id: 기업별 질문일 경우 job_id
            context: 추가 컨텍스트
        
        Returns:
            AnswerEvaluation: 평가 결과
        """
        # 질문 가져오기
        question = self.db.query(Question).get(question_id)
        if not question:
            raise ValueError(f"Question not found: {question_id}")
        
        # 컨텍스트 구성
        if context is None:
            context = self._build_evaluation_context(interview_id)
        
        # 답변 평가
        evaluation = await self.answer_scorer.evaluate_answer(
            question=question,
            answer_text=answer_text,
            context=context
        )
        
        return evaluation
    
    async def reevaluate_all_answers(
        self,
        interview_id: int
    ) -> List[AnswerEvaluation]:
        """
        면접 완료 후 모든 답변 재평가
        
        Args:
            interview_id: 면접 세션 ID
        
        Returns:
            List[AnswerEvaluation]: 재평가된 결과 리스트
        """
        # 세션 확인
        session = self.db.query(InterviewSession).get(interview_id)
        if not session:
            raise ValueError(f"Interview session not found: {interview_id}")
        
        # 모든 답변 가져오기
        results = self.db.query(InterviewResult).filter(
            InterviewResult.interview_id == interview_id
        ).all()
        
        if not results:
            return []
        
        # 각 답변 재평가
        evaluations = []
        context = self._build_evaluation_context(interview_id)
        
        for result in results:
            question = self.db.query(Question).get(result.question_id)
            if not question:
                continue
            
            # 재평가
            evaluation = await self.answer_scorer.evaluate_answer(
                question=question,
                answer_text=result.stt_full_text,
                context=context
            )
            
            # DB 업데이트
            result.scores = evaluation.scores
            result.keywords = {
                "matched": evaluation.matched_keywords,
                "missing": evaluation.missing_keywords
            }
            result.strengths = evaluation.strengths
            result.weaknesses = evaluation.weaknesses
            result.ai_feedback = evaluation.evaluation_detail
            result.updated_at = datetime.utcnow()
            
            evaluations.append(evaluation)
        
        self.db.commit()
        
        return evaluations
    
    def get_interview_results(
        self,
        interview_id: int
    ) -> List[InterviewResult]:
        """
        면접 세션의 모든 답변 조회
        
        Args:
            interview_id: 면접 세션 ID
        
        Returns:
            List[InterviewResult]: 답변 리스트
        """
        results = self.db.query(InterviewResult).filter(
            InterviewResult.interview_id == interview_id
        ).order_by(InterviewResult.created_at).all()
        
        return results
    
    def get_common_answers(
        self,
        interview_id: int
    ) -> List[InterviewResult]:
        """공통 질문 답변만 조회"""
        return self.db.query(InterviewResult).filter(
            InterviewResult.interview_id == interview_id,
            InterviewResult.is_common == True
        ).all()
    
    def get_company_answers(
        self,
        interview_id: int,
        job_id: int
    ) -> List[InterviewResult]:
        """특정 기업의 질문 답변만 조회"""
        return self.db.query(InterviewResult).filter(
            InterviewResult.interview_id == interview_id,
            InterviewResult.job_id == job_id
        ).all()
    
    def _build_evaluation_context(
        self,
        interview_id: int
    ) -> Dict[str, Any]:
        """평가 컨텍스트 생성"""
        session = self.db.query(InterviewSession).get(interview_id)
        if not session:
            return {}
        
        return {
            "applicant_id": session.applicant_id,
            "job_ids": session.job_ids,
            "session_id": interview_id
        }
    
    # ========== 전체 평가 메서드 (추가) ==========
    
    async def evaluate_full_interview(
        self,
        interview_id: int
    ) -> Dict[str, Any]:
        """
        면접 종료 후 전체 평가 및 매칭 점수 계산
        
        Args:
            interview_id: 면접 세션 ID
        
        Returns:
            기업별 매칭 점수 결과
        """
        from models.interview import Applicant, Company, InterviewStatus
        from models.job import Job
        from schemas.company import CompanyProfile
        from schemas.applicant import ApplicantProfile
        from schemas.interview import Question as QuestionSchema
        from ai.scorers.score_aggregator import ScoreAggregator
        
        # 1. 면접 세션 검증
        session = self.db.query(InterviewSession).get(interview_id)
        if not session:
            raise ValueError(f"Interview session not found: {interview_id}")
        
        if session.status != InterviewStatus.COMPLETED:
            raise ValueError(f"Interview must be COMPLETED, current: {session.status}")
        
        # 2. 지원자 프로필 조회
        applicant = self.db.query(Applicant).filter(
            Applicant.id == session.applicant_id
        ).first()
        
        if not applicant:
            raise ValueError(f"Applicant not found: {session.applicant_id}")
        
        applicant_profile = ApplicantProfile(
            id=applicant.id,
            skills=applicant.skills or [],
            total_experience_years=applicant.total_experience_years or 0,
            domain_experience=applicant.domain_experience or [],
            special_experience=applicant.special_experience or []
        )
        
        # 3. 선택한 기업들 조회
        selected_job_ids = session.job_ids or []  
        if not selected_job_ids:
            raise ValueError("No jobs selected for this interview")
        
        # 4. 모든 답변 조회
        answers = self.db.query(InterviewResult).filter( 
            InterviewResult.interview_id == interview_id
        ).all()
        
        if not answers:
            raise ValueError("No answers found for this interview")
        
        # 5. 공통 답변과 기업별 답변 분리
        common_answers = [ans for ans in answers if ans.is_common]
        company_answers_map = {}
        
        for ans in answers:
            if not ans.is_common and ans.job_id:
                if ans.job_id not in company_answers_map:
                    company_answers_map[ans.job_id] = []
                company_answers_map[ans.job_id].append(ans)
        
        # 6. 공통 답변 평가
        common_evaluations = []
        context = self._build_evaluation_context(interview_id)
        context["applicant_profile"] = applicant_profile.dict()
        
        for answer in common_answers:
            question = self.db.query(Question).filter(Question.id == answer.question_id).first()
            if not question:
                continue
            
            question_schema = QuestionSchema(
                id=question.id,
                job_id=question.job_id,
                question_text=question.question_text,
                question_type=question.question_type,
                evaluation_dimensions=question.evaluation_dimensions or [],
                dimension_weights=question.dimension_weights or {},
                expected_keywords=question.expected_keywords or [],
                difficulty_level=question.difficulty_level
            )
            
            evaluation = await self.answer_scorer.evaluate_answer(
                question=question_schema,
                answer_text=answer.stt_full_text, 
                context=context
            )
            
            common_evaluations.append(evaluation)
        
        # 7. 각 기업별로 평가 및 집계
        aggregator = ScoreAggregator()
        results = []
        
        for job_id in selected_job_ids:
            # Job 및 Company 조회
            job = self.db.query(Job).filter(Job.id == job_id).first()
            if not job:
                continue
            
            company = self.db.query(Company).filter(Company.id == job.company_id).first()
            if not company:
                continue
            
            # CompanyProfile 생성
            company_profile = CompanyProfile(
                id=company.id,
                name=company.name,
                core_values=company.core_values or [],
                category_weights=company.category_weights or {},
                priority_weights=company.priority_weights or {},
                required_skills=job.required_skills or [],
                preferred_skills=job.preferred_skills or [],
                min_years_experience=job.min_years_experience or 0,
                preferred_domains=job.preferred_domains or [],
                preferred_special_experience=job.preferred_special_experience or []
            )
            
            # 해당 기업 답변 평가
            company_evaluations = []
            company_specific_answers = company_answers_map.get(job_id, [])
            
            for answer in company_specific_answers:
                question = self.db.query(Question).filter(Question.id == answer.question_id).first()
                if not question:
                    continue
                
                question_schema = QuestionSchema(
                    id=question.id,
                    job_id=question.job_id,
                    question_text=question.question_text,
                    question_type=question.question_type,
                    evaluation_dimensions=question.evaluation_dimensions or [],
                    dimension_weights=question.dimension_weights or {},
                    expected_keywords=question.expected_keywords or [],
                    difficulty_level=question.difficulty_level
                )
                
                evaluation = await self.answer_scorer.evaluate_answer(
                    question=question_schema,
                    answer_text=answer.stt_full_text,  
                    context={
                        **context,
                        "company_profile": company_profile.dict()
                    }
                )
                
                company_evaluations.append(evaluation)
            
            # 점수 집계
            aggregated = aggregator.aggregate_for_company(
                common_answers=common_evaluations,
                company_answers=company_evaluations,
                company_profile=company_profile
            )
            
            results.append({
                "job_id": job_id,
                "company_id": company.id,
                "company_name": company.name,
                "aggregated_scores": aggregated.dict()
            })
        
        # 8. 면접 상태 업데이트
        session.evaluation_completed = True
        self.db.commit()
        
        return {
            "message": "Interview evaluation completed",
            "interview_id": interview_id,
            "applicant_id": applicant.id,
            "results": results
        }
    
    def get_evaluation_status(
        self,
        interview_id: int
    ) -> Dict[str, Any]:
        """
        면접 평가 상태 조회
        
        Args:
            interview_id: 면접 세션 ID
        
        Returns:
            평가 상태 정보
        """
        session = self.db.query(InterviewSession).get(interview_id)
        if not session:
            raise ValueError(f"Interview session not found: {interview_id}")
        
        total_answers = self.db.query(InterviewResult).filter( 
            InterviewResult.interview_id == interview_id
        ).count()
        
        return {
            "interview_id": interview_id,
            "status": session.status.value if hasattr(session.status, 'value') else str(session.status),
            "evaluation_completed": session.evaluation_completed,
            "total_answers": total_answers,
            "selected_jobs": session.job_ids or [] 
        }