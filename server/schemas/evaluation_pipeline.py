from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# --- 1. Transcript 세그먼트 형식 정의 ---
class TranscriptSegment(BaseModel):
    segment_id: int = Field(..., description="대화 세그먼트 고유 ID")
    segment_order: int = Field(..., description="세그먼트 순서")
    turn_type: str = Field("main", description="질문 유형 (main / follow_up)") # Default to 'main'
    question_text: str = Field(..., description="질문 내용")
    answer_text: str = Field(..., description="지원자의 답변 내용")
    answer_duration_sec: Optional[int] = Field(None, description="답변 길이 (초)")
    char_index_start: Optional[int] = Field(None, description="답변 텍스트의 시작 문자 인덱스")
    char_index_end: Optional[int] = Field(None, description="답변 텍스트의 끝 문자 인덱스")

class Transcript(BaseModel):
    metadata: Dict[str, Any] = Field(..., description="면접 Transcript 메타데이터")
    segments: List[TranscriptSegment] = Field(..., description="질문-답변 세그먼트 리스트")

# --- 2. 개별 에이전트 결과 구조 (1차, 2차 공통) ---
class AgentConfidence(BaseModel):
    overall_confidence: float = Field(..., ge=0, le=1, description="해당 역량 평가의 전반적인 신뢰도 (0~1)")
    evidence_strength: Optional[float] = Field(None, ge=0, le=1, description="근거 자료의 강도 (0~1)")
    internal_consistency: Optional[float] = Field(None, ge=0, le=1, description="평가 내용의 내부 일관성 (0~1)")
    
class AgentEvaluationResult(BaseModel):
    competency_name: str = Field(..., description="평가된 역량의 이름")
    competency_display_name: str = Field(..., description="역량의 사용자 친화적 이름") # for UI
    score: float = Field(..., ge=0, le=100, description="역량 점수 (0~100)")
    reasoning: str = Field(..., description="점수 및 평가에 대한 상세 근거")
    strengths: List[str] = Field(default_factory=list, description="지원자의 강점 리스트")
    weaknesses: List[str] = Field(default_factory=list, description="지원자의 약점 리스트")
    confidence: AgentConfidence = Field(..., description="평가 신뢰도 정보")
    segments_evaluated: List[int] = Field(default_factory=list, description="이 역량 평가에 사용된 세그먼트 ID 리스트")
    
    # LLM 원본 응답 및 파싱된 구조 (S3에 저장될 내용)
    raw_llm_output: Optional[str] = Field(None, description="LLM의 원본 JSON 응답 (파싱 전)")
    parsed_llm_output: Optional[Dict[str, Any]] = Field(None, description="LLM의 응답이 Pydantic 스키마로 파싱된 형태")
    
    # 실행 메타데이터
    execution_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="에이전트 실행 관련 메타데이터 (모델명, 프롬프트 버전, 실행 시간 등)"
    )

# --- 3. Aggregator 출력 구조 (최종 통합 결과) ---
class ReasoningLogDetail(BaseModel):
    score: float = Field(..., ge=0, le=100, description="역량 점수 (0~100)")
    reasoning: str = Field(..., description="점수 및 평가에 대한 상세 근거")
    strengths: List[str] = Field(default_factory=list, description="지원자의 강점 리스트")
    weaknesses: List[str] = Field(default_factory=list, description="지원자의 약점 리스트")
    confidence: AgentConfidence = Field(..., description="평가 신뢰도 정보")

class ValidationResult(BaseModel):
    status: str = Field(..., description="검증 결과 상태 (OK, WARN, FAILED)")
    issues: List[str] = Field(default_factory=list, description="발견된 문제점 리스트")

class NormalizationMetadata(BaseModel):
    pipeline_version: str = Field(..., description="점수 정규화에 사용된 파이프라인 버전")
    weight_profile_version: str = Field(..., description="사용된 가중치 프로파일 버전")
    # job_avg: Optional[float] = None # 예시 필드
    # job_std: Optional[float] = None # 예시 필드

class EvaluationMetadata(BaseModel):
    llm_model_name: str = Field(..., description="최종 평가에 사용된 LLM 모델명")
    prompt_version: str = Field(..., description="최종 평가에 사용된 프롬프트 버전")
    aggregator_version: str = Field(..., description="Aggregator 로직 버전")
    # ... 기타 에이전트 메타데이터

class AggregatedEvaluationResult(BaseModel):
    interview_id: int = Field(..., description="면접 세션 ID")
    applicant_id: int = Field(..., description="지원자 ID")
    job_id: int = Field(..., description="직무 ID")
    
    # 최종 수치 계산
    match_score: float = Field(..., ge=0, le=100, description="직무 적합도 점수 (최종 0~100)")
    normalized_score: float = Field(..., ge=0, le=100, description="정규화된 종합 점수")
    weighted_score: float = Field(..., ge=0, le=100, description="가중치 적용 종합 점수")
    avg_confidence: float = Field(..., ge=0, le=1, description="종합 신뢰도 (0~1)")

    overall_feedback: str = Field(..., description="AI가 생성한 최종 종합 피드백")
    hiring_recommendation: str = Field(..., description="채용 추천 (예: STRONG_FIT, MODERATE_FIT)")
    
    # 세부 점수
    job_competency_scores: Dict[str, float] = Field(..., description="직무 역량별 최종 점수")
    common_competency_scores: Dict[str, float] = Field(..., description="공통 역량별 최종 점수")
    
    # 메타/로그 필드 (DB에 JSONB로 저장될 수 있음)
    reasoning_log: Dict[str, ReasoningLogDetail] = Field(..., description="각 역량별 상세 추론 로그")
    normalization_metadata: NormalizationMetadata = Field(..., description="정규화 및 가중치 적용 관련 메타데이터")
    evaluation_metadata: EvaluationMetadata = Field(..., description="평가 에이전트 관련 메타데이터")
    validation_result: ValidationResult = Field(..., description="최종 결과에 대한 일관성 검증 결과")

# --- S3에 저장될 최종 평가 파일 (claim-check 패턴) ---
class S3FinalEvaluation(BaseModel):
    transcript_s3_key: str = Field(..., description="원본 Transcript S3 키")
    agent_raw_outputs_s3_key: Dict[str, str] = Field(..., description="각 에이전트의 원본 LLM 응답 및 파싱 결과 S3 키")
    aggregation_input_s3_key: str = Field(..., description="Aggregator 입력 데이터 S3 키")
    aggregation_result_s3_key: str = Field(..., description="Aggregator 최종 결과 S3 키")
    validation_report_s3_key: str = Field(..., description="유효성 검증 리포트 S3 키")
    hr_report_llm_output_s3_key: str = Field(..., description="HR 리포트용 LLM 출력 S3 키")
    
    final_evaluation_summary: AggregatedEvaluationResult = Field(..., description="최종 집계 평가 요약 (DB에 저장될 내용과 동일)")

    # + @ 최종 DB에 저장될 데이터에 S3 키 추가
