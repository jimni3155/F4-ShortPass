# app/schemas/interview.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class Question(BaseModel):
    """질문 스키마"""
    id: int
    job_id: Optional[int] = None  # NULL이면 공통 질문
    question_text: str
    question_type: str 
    
    # 평가 관련
    evaluation_competencies: List[str] = []
    competency_weights: Dict[str, float] = {}
    expected_keywords: List[str] = []
    difficulty_level: int = 3
    
    class Config:
        from_attributes = True


class AnswerEvaluation(BaseModel):
    """답변 평가 결과"""
    question_id: int
    question_text: str
    question_type: str
    answer_text: str
    
    # 질문의 가중치 정보 (평가 시 Question에서 복사)
    competencies_weights: Dict[str, float] = {}
    
    # 평가 결과
    scores: Dict[str, float]  # {"python": 85, "system_design": 90, ...}
    evaluation_detail: str = ""
    matched_keywords: List[str] = []
    missing_keywords: List[str] = []
    strengths: List[str] = []
    weaknesses: List[str] = []


class CompetencyScore(BaseModel):
    """역량 점수 상세 정보"""
    score: float = Field(0.0, ge=0, le=100, description="역량 점수")
    sub_scores: Dict[str, float] = Field(default_factory=dict, description="하위 차원 점수")
    mentioned_items: List[str] = Field(default_factory=list, description="언급된 키워드")
    evaluation_count: int = Field(0, description="평가된 답변 개수")


class AggregatedScores(BaseModel):
    """6개 역량별 집계 점수"""
    job_expertise: CompetencyScore = Field(default_factory=CompetencyScore)
    problem_solving: CompetencyScore = Field(default_factory=CompetencyScore)
    organizational_fit: CompetencyScore = Field(default_factory=CompetencyScore)
    growth_potential: CompetencyScore = Field(default_factory=CompetencyScore)
    interpersonal_skill: CompetencyScore = Field(default_factory=CompetencyScore)
    achievement_motivation: CompetencyScore = Field(default_factory=CompetencyScore)
    
    def get_competency_score(self, competency_key: str) -> float:
        """특정 역량 점수 반환"""
        return getattr(self, competency_key, CompetencyScore()).score
    
    def get_all_scores(self) -> Dict[str, float]:
        """모든 역량 점수를 dict로 반환"""
        return {
            "job_expertise": self.job_expertise.score,
            "problem_solving": self.problem_solving.score,
            "organizational_fit": self.organizational_fit.score,
            "growth_potential": self.growth_potential.score,
            "interpersonal_skill": self.interpersonal_skill.score,
            "achievement_motivation": self.achievement_motivation.score
        }



# ========== Request/Response ==========

class PrepareInterviewRequest(BaseModel):
    """면접 준비 요청 - 단일 회사 + 순차 페르소나"""
    candidateId: str = Field(..., description="지원자 ID")
    companyId: str = Field(..., description="선택된 회사 ID")
    personaInstanceIds: List[str] = Field(..., description="페르소나 인스턴스 ID 리스트 (순차 패널)")


class PrepareInterviewResponse(BaseModel):
    """면접 준비 응답"""
    interviewId: int = Field(..., description="생성된 면접 세션 ID")
    applicantId: int = Field(..., description="지원자 ID")
    companyId: int = Field(..., description="선택된 회사 ID")
    personaInstanceIds: List[int] = Field(..., description="페르소나 인스턴스 ID 리스트")
    status: str = Field(default="pending", description="면접 상태")
    message: str = Field(default="면접이 준비되었습니다.", description="응답 메시지")
    websocketUrl: str


class EvaluateAnswerRequest(BaseModel):
    """답변 평가 요청"""
    interview_id: int
    question_id: int
    answer_text: str = Field(..., min_length=1)
    is_common: bool = False
    job_id: Optional[int] = None