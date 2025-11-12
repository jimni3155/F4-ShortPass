# server/api/evaluation.py
"""
평가 및 매칭 결과 API (1:1 매칭, 근거 중심)
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from db.database import get_db
from services.evaluation_service import EvaluationService


router = APIRouter(prefix="/evaluations")


# 1. 평가 실행
@router.post("/execute")
async def execute_evaluation(
    interview_id: int = Query(...),
    job_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """면접 완료 후 평가 실행 (1:1 매칭)"""
    service = EvaluationService()
    
    try:
        result = await service.evaluate_applicant_for_job(
            db=db,
            applicant_id=None,
            job_id=job_id,
            interview_id=interview_id
        )
        return {
            "success": True,
            "evaluation_id": result["evaluation_id"],
            "match_score": result["match_score"],
            "normalized_score": result.get("normalized_score")  # 표준화 점수
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 2. 구직자용 - 평가 결과 조회
@router.get("/applicants/{applicant_id}/result/{evaluation_id}")
async def get_evaluation_result(
    applicant_id: int,
    evaluation_id: int,
    db: Session = Depends(get_db)
):
    """
    평가 결과 조회 (근거 포함)
    
    Returns:
        - 6개 역량별 점수
        - 각 역량별 근거 (evidence)
        - 루브릭 기반 평가 항목
        - 개선 제안
    """
    service = EvaluationService()
    
    try:
        return await service.get_evaluation_with_reasoning(
            db=db,
            applicant_id=applicant_id,
            evaluation_id=evaluation_id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# 3. 기업용 - 지원자 평가 조회
@router.get("/jobs/{job_id}/applicants/{applicant_id}/result")
async def get_applicant_evaluation_for_company(
    job_id: int,
    applicant_id: int,
    db: Session = Depends(get_db)
):
    """
    기업용 - 지원자 평가 상세 (근거 포함)
    
    Returns:
        - 6개 역량별 점수 + 근거
        - 루브릭 기반 평가 항목별 점수
        - AI 추론 로그 (reasoning log)
        - 채용 추천 + 리스크
        - 육성 계획
    """
    service = EvaluationService()
    
    try:
        return await service.get_company_evaluation_with_reasoning(
            db=db,
            job_id=job_id,
            applicant_id=applicant_id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/jobs/{job_id}/applicants")
async def get_all_applicants_for_job(
    job_id: int,
    min_score: float = Query(0, ge=0, le=100),
    db: Session = Depends(get_db)
):
    """기업용 - 모든 지원자 목록 (점수순, Blind)"""
    service = EvaluationService()
    
    try:
        return await service.get_job_applicants_summary(
            db=db,
            job_id=job_id,
            min_score=min_score
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# 4. 평가 통계 (편향 모니터링)
@router.get("/jobs/{job_id}/statistics")
async def get_job_evaluation_statistics(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    채용 공고별 평가 통계 (편향 모니터링용)
    
    Returns:
        - 평균/표준편차
        - 점수 분포
        - 역량별 평균
        - 편향 경고 (있을 경우)
    """
    service = EvaluationService()
    
    try:
        return await service.get_evaluation_statistics(
            db=db,
            job_id=job_id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/statistics/company/{company_id}")
async def get_company_evaluation_statistics(
    company_id: int,
    db: Session = Depends(get_db)
):
    """
    기업 전체 평가 통계 (편향 모니터링용)
    
    Returns:
        - 직무별 평균 점수
        - 정규화 지표
        - 편향 경고
    """
    service = EvaluationService()
    
    try:
        return await service.get_company_statistics(
            db=db,
            company_id=company_id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# 5. 관리자
@router.post("/{evaluation_id}/normalize")
async def normalize_evaluation_scores(
    evaluation_id: int,
    db: Session = Depends(get_db)
):
    """평가 점수 정규화 (편향 방지)"""
    service = EvaluationService()
    
    try:
        return await service.normalize_scores(
            db=db,
            evaluation_id=evaluation_id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/evaluations/{evaluation_id}/reasoning-log")
async def get_reasoning_log(
    evaluation_id: int,
    db: Session = Depends(get_db)
):
    """
    AI 추론 로그 조회 (디버깅/검증용)
    
    Returns:
        - 각 agent별 추론 과정
        - 근거 키워드
        - 신뢰도 점수
    """
    service = EvaluationService()
    
    try:
        return await service.get_reasoning_log(
            db=db,
            evaluation_id=evaluation_id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))