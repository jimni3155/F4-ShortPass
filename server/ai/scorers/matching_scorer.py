# server/ai/scorers/matching_scorer.py
"""
최종 매칭 점수 계산 - COMPETENCY 기반
"""
from typing import Dict, List
from schemas.interview import AggregatedScores
from schemas.company import CompanyProfile
from schemas.applicant import ApplicantProfile
from schemas.matching import MatchScore
from schemas.competencies import COMPETENCIES


class MatchingScorer:
    """집계된 역량 점수를 기반으로 최종 매칭 점수 계산"""
    
    def calculate_match(
        self,
        aggregated_scores: AggregatedScores,
        company_profile: CompanyProfile,
        applicant_profile: ApplicantProfile
    ) -> MatchScore:
        """
        최종 매칭 점수 계산
        
        개선 사항:
        - 반복 코드 제거
        - job_expertise 처리 분리
        - 명확한 단계별 처리
        """
        # 1. 면접 점수 추출 (6개 역량)
        competency_scores = aggregated_scores.get_all_scores()
        
        # 2. job_expertise만 이력서 결합 (면접 70% + 이력서 30%)
        competency_scores["job_expertise"] = self._enhance_job_expertise_with_resume(
            interview_score=competency_scores["job_expertise"],
            company_profile=company_profile,
            applicant_profile=applicant_profile
        )
        
        # 3. 가중치 가져오기
        weights = self._get_normalized_weights(company_profile)
        
        # 4. 최종 점수 = 가중 평균
        total_score = sum(
            competency_scores[key] * weights[key]
            for key in COMPETENCIES.keys()
        )
        
        # 5. 강점/약점 분석
        strengths = self._identify_strengths(competency_scores, aggregated_scores)
        weaknesses = self._identify_weaknesses(competency_scores, aggregated_scores, company_profile)
        
        return MatchScore(
            total_score=round(total_score, 2),
            job_expertise=round(competency_scores["job_expertise"], 2),
            problem_solving=round(competency_scores["problem_solving"], 2),
            organizational_fit=round(competency_scores["organizational_fit"], 2),
            growth_potential=round(competency_scores["growth_potential"], 2),
            interpersonal_skill=round(competency_scores["interpersonal_skill"], 2),
            achievement_motivation=round(competency_scores["achievement_motivation"], 2),
            strengths=strengths,
            weaknesses=weaknesses
        )
    
    def _enhance_job_expertise_with_resume(
        self,
        interview_score: float,
        company_profile: CompanyProfile,
        applicant_profile: ApplicantProfile
    ) -> float:
        """
        직무 전문성 점수를 이력서 정보로 보강
        
        개선 사항:
        - 메서드명 명확화
        - interview_score 파라미터로 받음 (집계 로직 분리)
        """
        # 이력서 기술 매칭
        resume_score = self._calculate_resume_skill_match(
            company_profile=company_profile,
            applicant_profile=applicant_profile
        )
        
        # 면접 70% + 이력서 30%
        return interview_score * 0.7 + resume_score * 0.3
    
    def _calculate_resume_skill_match(
        self,
        company_profile: CompanyProfile,
        applicant_profile: ApplicantProfile
    ) -> float:
        """이력서 기술 매칭 점수"""
        applicant_skills = set(s.lower() for s in applicant_profile.skills)
        required_skills = set(s.lower() for s in company_profile.required_skills)
        preferred_skills = set(s.lower() for s in company_profile.preferred_skills)
        
        # 필수 기술 매칭률
        required_match_rate = (
            len(applicant_skills & required_skills) / len(required_skills)
            if required_skills else 1.0
        )
        
        # 우대 기술 매칭률
        preferred_match_rate = (
            len(applicant_skills & preferred_skills) / len(preferred_skills)
            if preferred_skills else 0.0
        )
        
        # 필수 90% + 우대 10%
        return required_match_rate * 90 + preferred_match_rate * 10
    
    def _get_normalized_weights(self, company_profile: CompanyProfile) -> Dict[str, float]:
        """
        정규화된 역량 가중치 반환
        
        개선 사항:
        - 메서드명 명확화 (정규화 명시)
        - 가중치 합 = 1 보장
        """
        if company_profile.competency_weights:
            weights = company_profile.competency_weights.copy()
        else:
            # 기본 가중치 (균등)
            num_competencies = len(COMPETENCIES)
            weights = {k: 1.0 / num_competencies for k in COMPETENCIES.keys()}
        
        # 정규화 (합 = 1)
        total = sum(weights.values())
        if total > 0:
            weights = {k: v / total for k, v in weights.items()}
        
        return weights
    
    def _identify_strengths(
        self,
        competency_scores: Dict[str, float],
        aggregated_scores: AggregatedScores
    ) -> List[str]:
        """강점 식별"""
        strengths = []
        
        # 1. 고득점 역량 (85점 이상)
        for competency_key, score in competency_scores.items():
            if score >= 85:
                competency_def = COMPETENCIES[competency_key]
                strengths.append(f"{competency_def.name}이(가) 매우 뛰어남")
        
        # 2. 세부 강점 (job_expertise의 키워드)
        if aggregated_scores.job_expertise.mentioned_items:
            top_items = aggregated_scores.job_expertise.mentioned_items[:3]
            for item in top_items:
                strengths.append(f"{item} 역량 보유")
        
        return strengths[:5]
    
    def _identify_weaknesses(
        self,
        competency_scores: Dict[str, float],
        aggregated_scores: AggregatedScores,
        company_profile: CompanyProfile
    ) -> List[str]:
        """약점 식별"""
        weaknesses = []
        
        # 1. 저득점 역량 (70점 미만)
        for competency_key, score in competency_scores.items():
            if score < 70:
                competency_def = COMPETENCIES[competency_key]
                weaknesses.append(f"{competency_def.name} 보완 필요")
        
        # 2. 부족한 필수 기술
        if competency_scores.get("job_expertise", 0) < 70:
            missing_skills = self._find_missing_required_skills(
                aggregated_scores=aggregated_scores,
                company_profile=company_profile
            )
            weaknesses.extend(missing_skills[:2])
        
        return weaknesses[:5]
    
    def _find_missing_required_skills(
        self,
        aggregated_scores: AggregatedScores,
        company_profile: CompanyProfile
    ) -> List[str]:
        """부족한 필수 기술 찾기"""
        mentioned = set(
            item.lower() 
            for item in aggregated_scores.job_expertise.mentioned_items
        )
        required = set(skill.lower() for skill in company_profile.required_skills)
        
        missing = required - mentioned
        return [f"{skill} 경험 부족" for skill in list(missing)[:3]]