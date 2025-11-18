# ai/agents/state.py
"""
LangGraph State 정의
모든 노드가 공유하는 상태
"""

from typing import TypedDict, Optional, Dict, Any, List
from datetime import datetime


class EvaluationState(TypedDict):
    """
    평가 과정에서 공유되는 상태
    """
    # 입력 데이터
    application_id: str
    interview_id: int
    job_id: int
    
    # 면접 및 지원자 정보
    interview_transcript: str  # 전체 면접 대화록
    applicant_resume: Dict[str, Any]  # 이력서 파싱 결과
    applicant_portfolio: Dict[str, Any]  # 포트폴리오 정보
    applicant_skills: List[str]  # 보유 기술
    applicant_experience_years: int  # 경력 연수
    
    # Job 정보
    job_description: str  # JD 전체 텍스트
    job_title: str
    required_skills: List[str]  # JD에서 추출한 필수 기술
    preferred_skills: List[str]  # 우대 기술
    domain_requirements: List[str]  # 도메인 요구사항
    dynamic_evaluation_criteria: List[str]  # 동적 평가 항목 (최대 5개)
    competency_weights: Dict[str, float]  # 역량별 가중치
    
    # 평가 기준표
    evaluation_standards: str  # 평가 기준표 텍스트
    
    # =================== Evaluator 결과 ===================
    job_expertise_result: Optional[Dict[str, Any]]
    analytical_result: Optional[Dict[str, Any]]
    execution_result: Optional[Dict[str, Any]]
    relationship_result: Optional[Dict[str, Any]]
    resilience_result: Optional[Dict[str, Any]]
    influence_result: Optional[Dict[str, Any]]

    # =================== Aggregator 결과 ===================
    aggregated_scores: Optional[Dict[str, float]]
    overall_feedback: Optional[str]
    key_insights: Optional[Dict[str, Any]]
    hiring_recommendation: Optional[str]
    recommendation_reasoning: Optional[str]
    job_requirement_fit_score: Optional[float]
    fit_analysis: Optional[str]
    expected_onboarding_duration: Optional[str]
    onboarding_support_needed: Optional[List[str]]

    
    # === 최종 추천 ===
    hiring_recommendation: Optional[str]  # 'strong_hire', 'hire', 'hold', 'no_hire'
    recommendation_reasoning: Optional[str]
    job_requirement_fit_score: Optional[float]
    fit_analysis: Optional[str]
    expected_onboarding_duration: Optional[str]
    onboarding_support_needed: Optional[List[str]]
    
    # === Adversarial Validation (향후 추가) ===
    # adversarial_challenges: Optional[Dict[str, Any]]
    # refined_scores: Optional[Dict[str, Any]]
    
    # 메타 정보
    evaluation_status: str  # 'pending', 'evaluating', 'aggregating', 'completed', 'failed'
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    # 성능 모니터링
    execution_logs: List[Dict[str, Any]]  # 각 노드 실행 시간 기록
    structured_transcript: Optional[List[Dict[str, Any]]] # 구조화된 면접 대화록 (발언별 메타데이터 포함)