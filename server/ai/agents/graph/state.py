"""
LangGraph State 정의
모든 노드가 공유하는 상태
"""
import operator
from typing import Dict, List, Optional, TypedDict, Any, Annotated
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
    
    # Job/Common 최종 통합 비율
    job_common_ratio: Dict[str, float]
    
    # 1단계_개별 역량 평가 결과 (10개)
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
    
    # 2단계_문제 탐지 결과
    # Evidence 충돌 목록
    evidence_conflicts: List[Dict]

    # 협업 필요 여부
    requires_collaboration: bool

    #3단계_협업 결과
    # Evidence 충돌 중재 결과
    mediation_results: List[Dict]

    
    # Adversarial 재평가 결과 (confidence 낮은 역량 대상)
    adversarial_results: List[Dict]
    

    # 협업 처리 횟수
    collaboration_count: int

    # 4단계__최종 통합 결과
    # Low Confidence 목록
    low_confidence_list: List[Dict]

    # 통합 결과
    # Job/Common 통합
    job_aggregation_result: Optional[Dict]
    common_aggregation_result: Optional[Dict]
    
    # 최종 점수 (Job + Common)
    final_score: Optional[float]
    
    # 신뢰도 정보
    avg_confidence: Optional[float]  # 10개 역량 평균 Confidence
    final_reliability: Optional[str]  # "매우 높음", "높음", "중간", "낮음"
    reliability_note: Optional[str]   # 신뢰도 근거 설명
    
    # 검증 결과 (기존)
    low_confidence_competencies: List[str]  # 역량명만 (기존 validator 호환)
    validation_notes: Optional[str]
    requires_revaluation: bool  # deprecated (Phase 2에서 처리)
    
    # 최종 결과 (전체)
    final_result: Optional[Dict]
    
    # 메타 정보
    started_at: datetime
    completed_at: Optional[datetime]
    errors: List[str]
    
    # 성능 모니터링
    execution_logs: Annotated[List[Dict[str, Any]], operator.add]  

    structured_transcript: Optional[List[Dict[str, Any]]]