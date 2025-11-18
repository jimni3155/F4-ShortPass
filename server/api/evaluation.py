"""
평가 API 엔드포인트 (LangGraph 기반)
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Optional, List
from datetime import datetime

from services.evaluation.evaluation_service import EvaluationService
from db.database import get_db
from models.evaluation import Evaluation

router = APIRouter(prefix="/evaluations", tags=["Evaluations"])

# 서비스 초기화
evaluation_service = EvaluationService()


# ==================== Schemas ====================

class TranscriptSegment(BaseModel):
    """Transcript Segment"""
    segment_id: int
    segment_order: int
    question_text: str
    answer_text: str
    answer_duration_sec: int
    char_index_start: int
    char_index_end: int


class Transcript(BaseModel):
    """면접 전사"""
    metadata: Dict
    segments: List[TranscriptSegment]


class EvaluationRequest(BaseModel):
    """평가 요청"""
    interview_id: int
    applicant_id: int
    job_id: int
    transcript: Transcript
    job_weights: Optional[Dict[str, float]] = None
    common_weights: Optional[Dict[str, float]] = None


class EvaluationStatusResponse(BaseModel):
    """평가 상태 응답"""
    evaluation_id: int
    status: str  # processing, completed, failed
    message: Optional[str] = None
    job_score: Optional[float] = None
    common_score: Optional[float] = None
    created_at: str
    completed_at: Optional[str] = None


# ==================== 1. 평가 생성 및 실행 ====================

@router.post("/", response_model=dict)
async def create_evaluation(
    request: EvaluationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    평가 생성 및 백그라운드 실행
    
    Flow:
    1. DB에 평가 레코드 생성 (status: processing)
    2. 백그라운드로 LangGraph 실행
    3. 즉시 evaluation_id 반환
    
    Returns:
        {
            "evaluation_id": 1,
            "status": "processing",
            "message": "평가가 시작되었습니다"
        }
    """
    
    try:
        # 1. DB에 평가 레코드 생성
        evaluation = Evaluation(
            interview_id=request.interview_id,
            applicant_id=request.applicant_id,
            job_id=request.job_id,
            status="processing",
            created_at=datetime.now()
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        
        # 2. 기본 가중치 설정
        job_weights = request.job_weights or {
            "structured_thinking": 0.25,
            "business_documentation": 0.20,
            "financial_literacy": 0.20,
            "industry_learning": 0.20,
            "stakeholder_management": 0.15
        }
        
        common_weights = request.common_weights or {
            "problem_solving": 0.25,
            "organizational_fit": 0.20,
            "growth_potential": 0.20,
            "interpersonal_skills": 0.20,
            "achievement_motivation": 0.15
        }
        
        # 3. 백그라운드 작업 등록
        background_tasks.add_task(
            run_evaluation_background,
            evaluation_id=evaluation.id,
            interview_id=request.interview_id,
            applicant_id=request.applicant_id,
            job_id=request.job_id,
            transcript=request.transcript.dict(),
            job_weights=job_weights,
            common_weights=common_weights,
            db=db
        )
        
        return {
            "evaluation_id": evaluation.id,
            "status": "processing",
            "message": "평가가 시작되었습니다. 약 3-5초 소요됩니다."
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"평가 생성 실패: {str(e)}")


# ==================== 2. 평가 상태 조회 ====================

@router.get("/{evaluation_id}", response_model=EvaluationStatusResponse)
async def get_evaluation_status(
    evaluation_id: int,
    db: Session = Depends(get_db)
):
    """
    평가 상태 조회
    
    Returns:
        {
            "evaluation_id": 1,
            "status": "completed",
            "job_score": 75.5,
            "common_score": 72.3,
            "created_at": "2025-01-15T10:00:00",
            "completed_at": "2025-01-15T10:00:05"
        }
    """
    
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    
    if not evaluation:
        raise HTTPException(status_code=404, detail="평가를 찾을 수 없습니다")
    
    return EvaluationStatusResponse(
        evaluation_id=evaluation.id,
        status=evaluation.status,
        message=evaluation.error_message if evaluation.status == "failed" else None,
        job_score=evaluation.job_score,
        common_score=evaluation.common_score,
        created_at=evaluation.created_at.isoformat(),
        completed_at=evaluation.completed_at.isoformat() if evaluation.completed_at else None
    )


# ==================== 3. 평가 상세 결과 조회 ====================

@router.get("/{evaluation_id}/detail")
async def get_evaluation_detail(
    evaluation_id: int,
    db: Session = Depends(get_db)
):
    """
    평가 상세 결과 조회 (10개 역량 전체)
    
    Returns:
        {
            "evaluation_id": 1,
            "status": "completed",
            "job_aggregation": {...},
            "common_aggregation": {...},
            "validation": {...}
        }
    """
    
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    
    if not evaluation:
        raise HTTPException(status_code=404, detail="평가를 찾을 수 없습니다")
    
    if evaluation.status != "completed":
        raise HTTPException(status_code=400, detail=f"평가가 완료되지 않았습니다 (상태: {evaluation.status})")
    
    return {
        "evaluation_id": evaluation.id,
        "status": evaluation.status,
        "job_aggregation": evaluation.job_aggregation_result,
        "common_aggregation": evaluation.common_aggregation_result,
        "validation": evaluation.validation_result,
        "created_at": evaluation.created_at.isoformat(),
        "completed_at": evaluation.completed_at.isoformat()
    }


# ==================== 4. 지원자별 평가 목록 ====================

@router.get("/applicants/{applicant_id}")
async def get_evaluations_by_applicant(
    applicant_id: int,
    db: Session = Depends(get_db)
):
    """
    지원자별 평가 목록 조회
    
    Returns:
        {
            "applicant_id": 1,
            "total_evaluations": 3,
            "evaluations": [...]
        }
    """
    
    evaluations = db.query(Evaluation).filter(
        Evaluation.applicant_id == applicant_id
    ).order_by(Evaluation.created_at.desc()).all()
    
    return {
        "applicant_id": applicant_id,
        "total_evaluations": len(evaluations),
        "evaluations": [
            {
                "evaluation_id": e.id,
                "job_id": e.job_id,
                "status": e.status,
                "job_score": e.job_score,
                "common_score": e.common_score,
                "created_at": e.created_at.isoformat()
            }
            for e in evaluations
        ]
    }


# ==================== 5. 직무별 평가 목록 ====================

@router.get("/jobs/{job_id}")
async def get_evaluations_by_job(
    job_id: int,
    min_score: Optional[float] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    직무별 평가 목록 조회 (필터링 가능)
    
    Query Params:
        - min_score: 최소 점수 필터
        - status: 상태 필터 (processing, completed, failed)
    
    Returns:
        {
            "job_id": 1,
            "total_evaluations": 10,
            "evaluations": [...]
        }
    """
    
    query = db.query(Evaluation).filter(Evaluation.job_id == job_id)
    
    if status:
        query = query.filter(Evaluation.status == status)
    
    if min_score is not None:
        query = query.filter(
            (Evaluation.job_score + Evaluation.common_score) / 2 >= min_score
        )
    
    evaluations = query.order_by(Evaluation.created_at.desc()).all()
    
    return {
        "job_id": job_id,
        "total_evaluations": len(evaluations),
        "evaluations": [
            {
                "evaluation_id": e.id,
                "applicant_id": e.applicant_id,
                "status": e.status,
                "job_score": e.job_score,
                "common_score": e.common_score,
                "average_score": (e.job_score + e.common_score) / 2 if e.job_score and e.common_score else None,
                "created_at": e.created_at.isoformat()
            }
            for e in evaluations
        ]
    }


# ==================== 백그라운드 작업 ====================

async def run_evaluation_background(
    evaluation_id: int,
    interview_id: int,
    applicant_id: int,
    job_id: int,
    transcript: Dict,
    job_weights: Dict[str, float],
    common_weights: Dict[str, float],
    db: Session
):
    """백그라운드에서 실행되는 평가 함수"""
    
    try:
        print(f"\n[백그라운드] Evaluation #{evaluation_id} 시작")
        
        # 평가 실행
        result = await evaluation_service.evaluate_interview(
            interview_id=interview_id,
            applicant_id=applicant_id,
            job_id=job_id,
            transcript=transcript,
            job_weights=job_weights,
            common_weights=common_weights
        )
        
        # DB 업데이트
        evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
        
        evaluation.status = "completed"
        evaluation.job_score = result["job_aggregation"]["overall_job_score"]
        evaluation.common_score = result["common_aggregation"]["overall_common_score"]
        evaluation.job_aggregation_result = result["job_aggregation"]
        evaluation.common_aggregation_result = result["common_aggregation"]
        evaluation.validation_result = result["validation"]
        evaluation.completed_at = datetime.now()
        
        db.commit()
        
        print(f"[백그라운드] Evaluation #{evaluation_id} 완료")
        print(f"  - Job 점수: {evaluation.job_score}")
        print(f"  - Common 점수: {evaluation.common_score}")
        
    except Exception as e:
        print(f"[백그라운드 오류] Evaluation #{evaluation_id}: {e}")
        
        # 실패 상태 업데이트
        evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
        evaluation.status = "failed"
        evaluation.error_message = str(e)
        db.commit()