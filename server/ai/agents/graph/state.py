# server/ai/agents/graph/state.py
"""
LangGraph State 정의
모든 노드가 공유하는 상태
"""
from typing import Dict, List, Optional, TypedDict, Any
from datetime import datetime


class EvaluationState(TypedDict):
    """평가 프로세스 전체 상태"""
    
    # 입력 데이터
    interview_id: int
    applicant_id: int
    job_id: int
    transcript: Dict  # JSON 형태의 전체 transcript
    openai_client: Any  
    prompts: Dict[str, str]  # 10개 역량별 프롬프트
    
    # 가중치 (JD 파싱 결과)
    job_weights: Dict[str, float]  # Job 5개 역량 가중치
    common_weights: Dict[str, float]  # Common 5개 역량 가중치
    
    # 개별 역량 평가 결과 (10개)
    structured_thinking_result: Optional[Dict]
    business_documentation_result: Optional[Dict]
    financial_literacy_result: Optional[Dict]
    industry_learning_result: Optional[Dict]
    stakeholder_management_result: Optional[Dict]
    problem_solving_result: Optional[Dict]
    organizational_fit_result: Optional[Dict]
    growth_potential_result: Optional[Dict]
    interpersonal_skills_result: Optional[Dict]
    achievement_motivation_result: Optional[Dict]
    
    # 통합 결과
    job_aggregation_result: Optional[Dict]
    common_aggregation_result: Optional[Dict]
    
    # 검증 결과
    low_confidence_competencies: List[str]
    validation_notes: Optional[str]
    requires_revaluation: bool
    
    # 최종 결과 (추후)
    final_result: Optional[Dict]
    
    # 메타 정보
    started_at: datetime
    completed_at: Optional[datetime]
    errors: List[str]
    
    # 성능 모니터링
    execution_logs: List[Dict[str, Any]]  # 각 노드 실행 시간 기록
    structured_transcript: Optional[List[Dict[str, Any]]] # 구조화된 면접 대화록 (발언별 메타데이터 포함)