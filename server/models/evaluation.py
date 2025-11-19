# server/models/evaluation.py
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Index, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base


class Evaluation(Base):
    """
    Evaluation 테이블 - Multiagent 평가 결과 (1:1 매칭, 근거 저장)
    """
    __tablename__ = "evaluations"
    
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Keys
    applicant_id = Column(Integer, ForeignKey("applicants.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    interview_id = Column(Integer, ForeignKey("interview_sessions.id", ondelete="SET NULL"), nullable=True, index=True)

    # Status
    evaluation_status = Column(Text, nullable=False, default="PENDING")  # PENDING, PROCESSING, COMPLETED, FAILED
    error_message = Column(Text, nullable=True)
    
    # ===== 핵심 점수 =====
    match_score = Column(Float, nullable=False, index=True)  # 원점수 (0-100)
    normalized_score = Column(Float, nullable=True, index=True)  # 표준화 점수 (편향 방지)
    weighted_score = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)

    # ===== 종합 피드백 =====
    overall_feedback = Column(Text, nullable=True)  # 전체 피드백
    hiring_recommendation = Column(Text, nullable=True)  # 채용 추천 (STRONG_FIT, MODERATE_FIT, WEAK_FIT)
    recommendation_reasoning = Column(Text, nullable=True)  # 추천 근거
    
    # ===== 6개 고정 역량 점수 (Float) =====
    job_expertise = Column(Float, nullable=True)  # 직무 전문성
    analytical = Column(Float, nullable=True)  # 분석력
    execution = Column(Float, nullable=True)  # 실행력
    relationship_building = Column("relationship", Float, nullable=True)  # 관계 구축 (고객 집착) - DB 컬럼명: relationship
    resilience = Column(Float, nullable=True)  # 회복탄력성 (학습 태도)
    influence = Column(Float, nullable=True)  # 영향력

    # ===== 기타 역량 점수 =====
    problem_solving = Column(Float, nullable=True)
    organizational_fit = Column(Float, nullable=True)
    growth_potential = Column(Float, nullable=True)
    interpersonal_skills = Column(Float, nullable=True)
    achievement_motivation = Column(Float, nullable=True)
    structured_thinking = Column(Float, nullable=True)
    business_documentation = Column(Float, nullable=True)
    financial_literacy = Column(Float, nullable=True)
    industry_learning = Column(Float, nullable=True)
    stakeholder_management = Column(Float, nullable=True)

    # ===== 통합 점수 =====
    job_aggregation = Column(Float, nullable=True)
    common_aggregation = Column(Float, nullable=True)

    # ===== Fit 분석 =====
    job_requirement_fit_score = Column(Float, nullable=True)
    fit_analysis = Column(Text, nullable=True)
    expected_onboarding_duration = Column(Text, nullable=True)
    onboarding_support_needed = Column(Text, nullable=True)
    key_insights = Column(JSON, nullable=True)

    # ===== 상세 결과 (JSON) =====
    competency_scores = Column(JSON, nullable=True)
    individual_evaluations = Column(JSON, nullable=True)
    aggregated_evaluation = Column(JSON, nullable=True)
    match_result = Column(JSON, nullable=True)
    validation_result = Column(JSON, nullable=True)  # 신뢰도 검증 결과

    # ===== S3 참조 (Claim Check Pattern) =====
    agent_logs_s3_url = Column(Text, nullable=True)  # S3 execution logs 경로

    # ===== 근거 저장 (레거시) =====
    reasoning_log = Column(JSON, nullable=True)  # AI 추론 과정 로그 (레거시)
    """
    {
        "job_expertise": {
            "reasoning": "Python 3년 경험, AWS 실무 프로젝트 2개...",
            "evidence_keywords": ["Python", "AWS", "Docker"],
            "confidence": 0.85
        },
        ...
    }
    """
    
    rubric_scores = Column(JSON, nullable=True)  # 루브릭 기반 평가 점수
    """
    {
        "논리성": {"score": 90, "evidence": "..."},
        "명확성": {"score": 85, "evidence": "..."},
        "협업력": {"score": 75, "evidence": "..."}
    }
    """
    
    # ===== 정규화 정보 (편향 방지) =====
    normalization_metadata = Column(JSON, nullable=True)
    """
    {
        "job_avg": 75.3,
        "job_std": 8.2,
        "company_avg": 78.5,
        "normalized_at": "2025-11-10T12:00:00Z"
    }
    """
    
    # ===== 메타데이터 =====
    evaluation_metadata = Column(JSON, nullable=True)
    
    # ===== 타임스탬프 =====
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # ===== Relationships ===== (주석 처리: 다른 모델과의 충돌 방지)
    # applicant = relationship("Applicant", backref="evaluations")
    # job = relationship("Job", backref="evaluations")
    # interview = relationship("InterviewSession", backref="evaluations")
    
    # ===== Indexes =====
    __table_args__ = (
        Index('ix_evaluations_job_match_score', 'job_id', 'match_score'),
        Index('ix_evaluations_job_normalized_score', 'job_id', 'normalized_score'),
        Index('ix_evaluations_applicant_created', 'applicant_id', 'created_at'),
    )