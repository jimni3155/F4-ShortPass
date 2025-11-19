"""
Unified Competency Evaluation Schema
모든 역량(Job-specific + Common) 평가에 사용되는 통합 스키마
"""

from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, validator


# ============================================
# Evidence Perspective Components
# ============================================

class EvidenceDetail(BaseModel):
    """개별 증거 (Quote) 상세"""
    text: str = Field(..., description="인터뷰 transcript에서 추출한 정확한 인용구")
    segment_id: int = Field(..., description="TranscriptSegment ID")
    char_index: int = Field(..., description="answer_text 내 시작 위치")
    relevance_note: str = Field(..., description="이 quote가 해당 역량과 관련된 이유")
    quality_score: float = Field(..., ge=0.0, le=1.0, description="Quote의 질적 수준 (0-1)")


class EvidencePerspective(BaseModel):
    """증거 기반 평가 관점"""
    score: float = Field(..., ge=0, le=100, description="Evidence 기반 점수 (0-100)")
    weight: float = Field(..., ge=0.0, le=1.0, description="Evidence 신뢰도 가중치")
    details: List[EvidenceDetail] = Field(..., min_items=0, description="추출된 Quote 목록")
    reasoning: str = Field(
        ...,
        description="⭐ 필수: '[점수 구간]에서 출발. [충족 기준]. [미충족 기준]. 따라서 [최종 점수].' 형식"
    )


# ============================================
# Behavioral Perspective Components
# ============================================

class BehavioralPattern(BaseModel):
    """관찰된 행동 패턴"""
    pattern_description: str = Field(..., description="관찰된 핵심 패턴 (예: 자발성, 끈기, 논리 구조)")
    specific_examples: List[str] = Field(
        ...,
        min_items=1,
        description="구체적 예시 목록 (반드시 segment_id 포함)"
    )
    consistency_note: str = Field(..., description="패턴의 일관성 평가")


class BehavioralPerspective(BaseModel):
    """행동 패턴 기반 평가 관점"""
    score: float = Field(..., ge=0, le=100, description="Behavioral 패턴 점수 (0-100)")
    pattern: BehavioralPattern = Field(..., description="관찰된 행동 패턴 상세")
    reasoning: str = Field(
        ...,
        description="⭐ 필수: '[점수 구간]. [관찰된 패턴]. [일관성]. 따라서 [점수].' 형식"
    )


# ============================================
# Critical Perspective Components
# ============================================

class RedFlag(BaseModel):
    """발견된 문제점 (Red Flag)"""
    flag_type: str = Field(
        ...,
        description="Flag 유형 (예: external_motivation_only, illogical_reasoning, resume_mismatch 등)"
    )
    description: str = Field(..., description="구체적인 문제 설명")
    severity: Literal["minor", "moderate", "severe"] = Field(..., description="심각도")
    penalty: int = Field(..., le=0, description="감점 (음수)")
    evidence_reference: str = Field(..., description="문제 발생 위치 (segment_id + char_index)")


class CriticalPerspective(BaseModel):
    """비판적 검증 관점"""
    penalties: int = Field(..., le=0, description="총 감점 (음수)")
    red_flags: List[RedFlag] = Field(default_factory=list, description="발견된 Red Flags")
    reasoning: str = Field(
        ...,
        description="⭐ 필수: 'Red Flag [개수]건. [각 Flag 설명].    총 감점 [점수].' 형식"
    )


# ============================================
# Integrated Perspectives
# ============================================

class EvaluationPerspectives(BaseModel):
    """3-Perspective 통합 평가"""
    evidence: EvidencePerspective = Field(..., description="증거 기반 평가")
    behavioral: BehavioralPerspective = Field(..., description="행동 패턴 평가")
    critical: CriticalPerspective = Field(..., description="비판적 검증")


# ============================================
# Confidence & Calculation
# ============================================

class ConfidenceMetrics(BaseModel):
    """평가 신뢰도 지표"""
    evidence_strength: float = Field(..., ge=0.0, le=1.0, description="증거 강도")
    internal_consistency: float = Field(..., ge=0.0, le=1.0, description="내적 일관성")
    overall_confidence: float = Field(..., ge=0.0, le=1.0, description="종합 신뢰도")
    confidence_note: str = Field(..., description="신뢰도 종합 설명")


class ScoreCalculation(BaseModel):
    """점수 계산 과정"""
    base_score: float = Field(..., description="Evidence score (시작점)")
    evidence_weight: float = Field(..., description="Evidence 가중치")
    behavioral_adjustment: float = Field(..., description="Behavioral 조정 계수 (0.8-1.2)")
    adjusted_base: float = Field(..., description="조정된 기본 점수")
    critical_penalties: int = Field(..., description="총 감점")
    final_score: float = Field(..., description="최종 점수 (0-100)")
    formula: str = Field(..., description="계산식 문자열 (예: '85 × 0.8 × 0.94 - 5 = 58.9')")


# ============================================
# Main Evaluation Schema
# ============================================

class CompetencyEvaluation(BaseModel):
    """
    통합 역량 평가 스키마
    
    Job-specific 역량(동적 생성) + Common 역량 모두 사용
    """
    # Metadata
    competency_name: str = Field(
        ...,
        description="역량 식별자 (예: job_expertise, problem_solving, achievement_motivation)"
    )
    competency_display_name: str = Field(..., description="역량 한글 표시명")
    competency_category: Literal["job", "common"] = Field(
        ...,
        description="역량 분류: job(직무 특화) | common(공통)"
    )
    evaluated_at: datetime = Field(..., description="평가 수행 시각 (ISO 8601)")
    
    # Core Evaluation
    perspectives: EvaluationPerspectives = Field(..., description="3-Perspective 통합 평가")
    
    # Final Results
    overall_score: float = Field(..., ge=0, le=100, description="최종 통합 점수 (0-100)")
    confidence: ConfidenceMetrics = Field(..., description="평가 신뢰도 지표")
    calculation: ScoreCalculation = Field(..., description="점수 계산 과정 상세")
    
    # Insights
    strengths: List[str] = Field(
        ...,
        min_items=1,
        description="강점 목록 (구체적 근거 포함, 예: '주도성 중상 (교수님께 먼저 제안)')"
    )
    weaknesses: List[str] = Field(
        ...,
        min_items=0,
        description="약점 목록 (개선 가능 영역)"
    )
    key_observations: List[str] = Field(
        ...,
        min_items=1,
        description="주요 관찰 사항 (예: '신입 치고는 자발성 명확 (상위 30% 추정)')"
    )
    suggested_followup_questions: List[str] = Field(
        ...,
        min_items=0,
        max_items=5,
        description="추가 면접 질문 제안"
    )
    
    @validator('overall_score')
    def validate_overall_score(cls, v, values):
        """최종 점수가 0-100 범위 내인지 검증"""
        if not 0 <= v <= 100:
            raise ValueError(f"overall_score must be between 0 and 100, got {v}")
        return round(v, 1)
    
    @validator('calculation')
    def validate_calculation_consistency(cls, v, values):
        """계산 과정의 논리적 일관성 검증"""
        if 'perspectives' in values:
            evidence_score = values['perspectives'].evidence.score
            if abs(v.base_score - evidence_score) > 0.1:
                raise ValueError(
                    f"base_score ({v.base_score}) must match evidence.score ({evidence_score})"
                )
        return v


# ============================================
# Usage Example
# ============================================
# resume 관련 뺌 내가 안 고침 고려해서 봐줘요
SCHEMA_EXAMPLE = {
    "competency_name": "achievement_motivation",
    "competency_display_name": "성취/동기 역량",
    "competency_category": "common",
    "evaluated_at": "2025-01-15T10:30:00Z",
    
    "perspectives": {
        "evidence": {
            "score": 85.0,
            "weight": 0.8,
            "details": [
                {
                    "text": "교수님께 직접 제안해서 연구 프로젝트를 시작했어요. 궁금해서 먼저 물어봤고",
                    "segment_id": 3,
                    "char_index": 1200,
                    "relevance_note": "주도성 (먼저 제안), 내적 동기 (궁금해서)",
                    "quality_score": 0.95
                }
            ],
            "reasoning": "Evidence: 75-89점(Good) 구간에서 시작. 주도성 중상 (교수님께 직접 제안). 목표 난이도 중상 (비전공 학회 발표). 내적 동기 명확 ('궁금해서' 반복). Quote 4개. 85점 산정."
        },
        "behavioral": {
            "score": 82.0,
            "pattern": {
                "pattern_description": "모든 경험에서 자발적 시작, 끈기, 열정 표현 자주",
                "specific_examples": [
                    "모든 주요 경험(3개)에서 자발적 시작: '먼저' 반복 (Segment 3, 7, 11)",
                    "끈기 명확: 공모전 2회 탈락 후 재도전 (Segment 9)",
                    "완수율 높음: 5개 프로젝트 중 4개 완수 (80%)"
                ],
                "consistency_note": "모든 경험에서 일관된 자발성"
            },
            "reasoning": "Behavioral: 75-89점 구간. 모든 경험 자발적 시작. 끈기 명확. 완수율 80%. 82점."
        },
        "critical": {
            "penalties": -5,
            "red_flags": [
                {
                    "flag_type": "easy_goal",
                    "description": "일부 상황에서 도전 회피",
                    "severity": "minor",
                    "penalty": -5,
                    "evidence_reference": "segment_id: 9, char_index: 3450-3500"
                }
            ],
            "resume_match_score": 0.9,
            "reasoning": "Critical: Red Flag 1건. 도전 회피(-5점). Resume 일치도 0.9. 총 감점 -5점."
        }
    },
    
    "overall_score": 59.0,
    "confidence": {
        "evidence_strength": 0.8,
        "resume_match": 0.9,
        "internal_consistency": 0.85,
        "overall_confidence": 0.84,
        "confidence_note": "증거 충분, Resume 일치도 높음, 일관적"
    },
    "calculation": {
        "base_score": 85.0,
        "evidence_weight": 0.8,
        "behavioral_adjustment": 0.94,
        "adjusted_base": 63.9,
        "critical_penalties": -5,
        "final_score": 58.9,
        "formula": "85 × 0.8 × 0.94 - 5 = 58.9 → 59점"
    },
    
    "strengths": [
        "주도성 중상 (교수님께 먼저 제안)",
        "내적 동기 명확 ('궁금해서' 반복)",
        "높은 완수율 (80%)"
    ],
    "weaknesses": [
        "일부 도전 회피 경향",
        "완수율 90% 미달"
    ],
    "key_observations": [
        "신입 치고는 자발성 명확 (상위 30% 추정)",
        "실패 후 재도전 끈기",
        "Resume 일치도 높음"
    ],
    "suggested_followup_questions": [
        "스스로 목표를 설정하고 도전했던 경험은?",
        "가장 중요한 동기는 무엇인가요?"
    ]
}