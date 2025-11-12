# app/services/matching_service.py
"""
매칭 점수 계산 서비스
"""
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from schemas.matching import (
    CompanyMatchResult,
    ApplicantMatchResult,
    CompanyMatch,
    ApplicantMatch,
    MatchScore
)
from schemas.interview import AnswerEvaluation
from ai.scorers.score_aggregator import ScoreAggregator
from ai.scorers.matching_scorer import MatchingScorer
from models.interview import InterviewSession, InterviewResult, Company, Applicant, InterviewStatus
from models.job import Job


class MatchingService:
    """매칭 계산 및 순위 생성"""
    
    def __init__(
        self,
        db: Session,
        score_aggregator: ScoreAggregator,
        matching_scorer: MatchingScorer
    ):
        self.db = db
        self.score_aggregator = score_aggregator
        self.matching_scorer = matching_scorer
    
    async def calculate_applicant_matches(
        self,
        interview_id: int
    ) -> CompanyMatchResult:
        """
        지원자가 보는 결과: 여러 회사와의 매칭 점수
        
        Args:
            interview_id: 완료된 면접 세션 ID
        
        Returns:
            CompanyMatchResult: 회사별 매칭 점수 및 순위
        """
        # 1. 면접 세션 가져오기
        session = self.db.query(InterviewSession).filter(
            InterviewSession.id == interview_id,
            InterviewSession.status == InterviewStatus.COMPLETED
        ).first()
        
        if not session:
            raise ValueError(f"Completed interview session not found: {interview_id}")
        
        # 2. 지원자 프로필
        applicant = self.db.query(Applicant).get(session.applicant_id)
        if not applicant:
            raise ValueError(f"Applicant not found: {session.applicant_id}")
        
        applicant_profile = self._build_applicant_profile(applicant)
        
        # 3. 모든 답변 조회 (interview_id로)
        all_results = self.db.query(InterviewResult).filter(
            InterviewResult.interview_id == interview_id
        ).all()
        
        # 4. 공통 질문 답변 추출
        common_results = [r for r in all_results if r.is_common]
        common_answers = self._convert_to_answer_evaluations(common_results)
        
        # 5. 각 회사별 매칭 계산
        matches = []
        
        for job_id in session.job_ids:  # [101, 102, 103]
            # Job을 먼저 조회하고, 그 Job의 company_id로 Company 조회
            job = self.db.query(Job).filter(Job.id == job_id).first()
            if not job:
                continue

            company = self.db.query(Company).filter(Company.id == job.company_id).first()
            if not company:
                continue
            
            company_profile = self._build_company_profile(company)
            
            # 이 회사의 질문 답변만 추출
            company_results = [r for r in all_results if r.job_id == job_id]
            company_answers = self._convert_to_answer_evaluations(company_results)
            
            # 답변 집계
            aggregated = self.score_aggregator.aggregate_for_company(
                common_answers=common_answers,
                company_answers=company_answers,
                company_profile=company_profile
            )
            
            # 매칭 점수 계산
            match_score = self.matching_scorer.calculate_match(
                aggregated_scores=aggregated,
                company_profile=company_profile,
                applicant_profile=applicant_profile
            )
            
            matches.append(CompanyMatch(
                company_id=company.id,
                company_name=company.name,
                job_id=job_id,
                job_title=job.title if job else "개발자",
                match_score=match_score,
                rank=0  # 나중에 정렬 후 부여
            ))
        
        # 6. 점수 순으로 정렬 및 순위 부여
        matches.sort(key=lambda x: x.match_score.total_score, reverse=True)
        for idx, match in enumerate(matches):
            match.rank = idx + 1
        
        return CompanyMatchResult(
            applicant_id=session.applicant_id,
            applicant_name=applicant.name,
            interview_session_id=interview_id,
            interview_completed_at=session.completed_at,
            matches=matches
        )
    
    async def calculate_company_matches(
        self,
        job_id: int
    ) -> ApplicantMatchResult:
        """
        기업이 보는 결과: 여러 지원자와의 매칭 점수
        
        Args:
            job_id: 채용 공고 ID
        
        Returns:
            ApplicantMatchResult: 지원자별 매칭 점수 및 순위
        """
        # 1. 이 job_id를 선택한 모든 완료된 면접 세션
        sessions = self.db.query(InterviewSession).filter(
            InterviewSession.status == InterviewStatus.COMPLETED,
            InterviewSession.job_ids.contains([job_id])  # JSONB contains
        ).all()
        
        if not sessions:
            # job_id로 Job을 조회하고, 그 Job의 company_id로 Company 조회
            job = self.db.query(Job).filter(Job.id == job_id).first()
            company = None
            if job:
                company = self.db.query(Company).filter(Company.id == job.company_id).first()

            return ApplicantMatchResult(
                company_id=company.id if company else 0,
                company_name=company.name if company else "",
                job_id=job_id,
                applicants=[]
            )

        # 2. Job을 먼저 조회하고, 그 Job의 company_id로 Company 조회
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise ValueError(f"Job not found: {job_id}")

        company = self.db.query(Company).filter(Company.id == job.company_id).first()
        if not company:
            raise ValueError(f"Company not found for job_id: {job_id}")
        
        company_profile = self._build_company_profile(company)
        
        # 3. 각 지원자별 매칭 계산
        matches = []
        
        for session in sessions:
            # 지원자 프로필
            applicant = self.db.query(Applicant).get(session.applicant_id)
            if not applicant:
                continue
            
            applicant_profile = self._build_applicant_profile(applicant)
            
            # 모든 답변 조회
            all_results = self.db.query(InterviewResult).filter(
                InterviewResult.interview_id == session.id
            ).all()
            
            # 공통 질문 답변
            common_results = [r for r in all_results if r.is_common]
            common_answers = self._convert_to_answer_evaluations(common_results)
            
            # 이 회사의 질문 답변
            company_results = [r for r in all_results if r.job_id == job_id]
            company_answers = self._convert_to_answer_evaluations(company_results)
            
            # 답변 집계
            aggregated = self.score_aggregator.aggregate_for_company(
                common_answers=common_answers,
                company_answers=company_answers,
                company_profile=company_profile
            )
            
            # 매칭 점수 계산
            match_score = self.matching_scorer.calculate_match(
                aggregated_scores=aggregated,
                company_profile=company_profile,
                applicant_profile=applicant_profile
            )

            # Blind 처리
            blind = company.blind_mode or False
            
            matches.append(ApplicantMatch(
                applicant_id=session.applicant_id,
                applicant_name=applicant.name if not blind else f"지원자_{len(matches)+1:03d}",
                age=applicant.age if not blind else None,
                education=applicant.education if not blind else None,
                gender=applicant.gender if not blind else None,
                match_score=match_score,
                interview_summary=self._generate_summary(aggregated),
                highlights=match_score.strengths[:3] if match_score.strengths else [],
                rank=0
            ))
        
        # 4. 점수 순으로 정렬 및 순위 부여
        matches.sort(key=lambda x: x.match_score.total_score, reverse=True)
        for idx, match in enumerate(matches):
            match.rank = idx + 1
        
        return ApplicantMatchResult(
            company_id=company.id,
            company_name=company.name,
            job_id=job_id,
            applicants=matches,
            total_applicants=len(matches)
        )
    
    def _convert_to_answer_evaluations(
        self,
        results: List[InterviewResult]
    ) -> List[AnswerEvaluation]:
        """
        InterviewResult 모델 → AnswerEvaluation 스키마 변환
        """
        evaluations = []

        for result in results:
            # scores는 이미 JSONB dict 형태로 저장되어 있음
            scores = result.scores or {}

            evaluation = AnswerEvaluation(
                question_id=result.question_id,
                question_text=result.question_text or "",
                question_type=result.question_type or "unknown",
                answer_text=result.stt_full_text,
                scores=scores,
                evaluation_detail=result.ai_feedback or "",
                matched_keywords=result.keywords.get("matched", []) if result.keywords else [],
                missing_keywords=result.keywords.get("missing", []) if result.keywords else [],
                strengths=result.strengths or [],
                weaknesses=result.weaknesses or []
            )
            evaluations.append(evaluation)

        return evaluations
    
    def _build_company_profile(self, company: Company):
        """회사 모델 → CompanyProfile 변환"""
        from schemas.company import CompanyProfile

        # TODO: Job description 파싱에서 가져와야 함 (임시로 하드코딩)
        required_skills = ["Python", "FastAPI", "PostgreSQL", "System Design"]
        preferred_skills = ["React", "AWS", "Docker", "Kubernetes"]

        return CompanyProfile(
            id=company.id,
            name=company.name,
            core_values=company.core_values or [],
            category_weights=company.category_weights or {},
            priority_weights=company.priority_weights or {},
            # Job-related fields
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            min_years_experience=3,
            preferred_domains=["백엔드 개발", "시스템 설계"],
            preferred_special_experience=["대규모 트래픽 처리", "MSA 아키텍처"]
        )
    
    def _build_applicant_profile(self, applicant: Applicant):
        """지원자 모델 → ApplicantProfile 변환"""
        from schemas.applicant import ApplicantProfile

        return ApplicantProfile(
            id=applicant.id,
            skills=applicant.skills or [],
            total_experience_years=applicant.total_experience_years or 0,
            domain_experience=applicant.domain_experience or [],
            special_experience=applicant.special_experience or []
        )
    
    def _generate_summary(self, aggregated_scores) -> str:
        """집계 결과 기반 요약 생성"""
        tech_rating = aggregated_scores.technical_data.get("overall_rating", 0)
        cultural_rating = aggregated_scores.cultural_data.get("overall_rating", 0)
        
        if tech_rating >= 85 and cultural_rating >= 85:
            return "기술력과 문화 적합도 모두 뛰어남"
        elif tech_rating >= 85:
            return "뛰어난 기술 역량 보유"
        elif cultural_rating >= 85:
            return "조직 문화에 매우 잘 부합함"
        else:
            return "전반적으로 양호한 수준"
