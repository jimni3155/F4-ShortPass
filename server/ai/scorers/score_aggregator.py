# server/ai/scorers/score_aggregator.py
"""
면접 답변 집계 로직 - COMPETENCY 기반
"""
from typing import List, Dict, Any
from collections import defaultdict
from schemas.interview import AnswerEvaluation, AggregatedScores, CompetencyScore
from schemas.company import CompanyProfile
from schemas.competencies import COMPETENCIES


class ScoreAggregator:
    """답변들을 집계하여 6개 역량별 점수 산출"""
    
    def aggregate_for_company(
        self,
        common_answers: List[AnswerEvaluation],
        company_answers: List[AnswerEvaluation],
        company_profile: CompanyProfile
    ) -> AggregatedScores:
        """
        특정 기업 관점에서 답변 집계
        
        개선 사항:
        - setattr 제거, 명시적 생성
        - 타입 안정성 강화
        """
        all_answers = common_answers + company_answers
        
        # 명시적으로 각 역량 계산 (setattr 대신)
        return AggregatedScores(
            job_expertise=self._aggregate_competency("job_expertise", all_answers, company_profile),
            problem_solving=self._aggregate_competency("problem_solving", all_answers, company_profile),
            organizational_fit=self._aggregate_competency("organizational_fit", all_answers, company_profile),
            growth_potential=self._aggregate_competency("growth_potential", all_answers, company_profile),
            interpersonal_skill=self._aggregate_competency("interpersonal_skill", all_answers, company_profile),
            achievement_motivation=self._aggregate_competency("achievement_motivation", all_answers, company_profile)
        )
    
    def _aggregate_competency(
        self,
        competency_key: str,
        answers: List[AnswerEvaluation],
        company_profile: CompanyProfile
    ) -> CompetencyScore:
        """
        특정 역량의 점수 집계
        
        개선 사항:
        - 반환 타입 Dict → CompetencyScore (타입 안정성)
        """
        weighted_scores = []
        mentioned_items = set()
        sub_scores = defaultdict(list)
        
        for answer in answers:
            if competency_key not in answer.scores:
                continue
            
            competency_score = answer.scores[competency_key]
            
            # 가중치 계산
            question_weight = answer.competency_weights.get(competency_key, 1.0)
            company_weight = self._get_company_competency_weight(competency_key, company_profile)
            final_weight = question_weight * company_weight
            
            weighted_scores.append({
                "score": competency_score,
                "weight": final_weight,
                "weighted_score": competency_score * final_weight
            })
            
            if answer.matched_keywords:
                mentioned_items.update(answer.matched_keywords)
        
        # 가중 평균
        if weighted_scores:
            total_weighted = sum(s["weighted_score"] for s in weighted_scores)
            total_weight = sum(s["weight"] for s in weighted_scores)
            final_score = total_weighted / total_weight if total_weight > 0 else 0
        else:
            final_score = 0.0
        
        return CompetencyScore(
            score=round(min(final_score, 100), 2),
            sub_scores=dict(sub_scores),
            mentioned_items=list(mentioned_items),
            evaluation_count=len(weighted_scores)
        )
    
    def _get_company_competency_weight(
        self,
        competency_key: str,
        company_profile: CompanyProfile
    ) -> float:
        """기업의 역량별 가중치"""
        if not company_profile.competency_weights:  # category_weights → competency_weights
            return 1.0 / len(COMPETENCIES)
        
        return company_profile.competency_weights.get(competency_key, 0.1)