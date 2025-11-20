"""
Evaluation List API - 지원자 목록 및 상세 조회
간단한 버전: 기존 코드 수정 없이 필요한 엔드포인트만 제공
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, text
from db.database import get_db
import logging

router = APIRouter(prefix="/evaluations")
logger = logging.getLogger("uvicorn")


@router.get("/jobs/{job_id}/applicants")
async def get_applicants_list(
    job_id: int,
    db: Session = Depends(get_db)
):
    """지원자 목록 조회 (간단 버전)"""
    logger.info(f"Getting applicants list for job ID: {job_id}")
    # Raw SQL로 간단하게 조회
    query = text("""
        SELECT
            e.id as evaluation_id,
            e.applicant_id,
            a.name as applicant_name,
            e.match_score as overall_score,
            e.normalized_score,
            e.created_at
        FROM evaluations e
        JOIN applicants a ON e.applicant_id = a.id
        WHERE e.job_id = :job_id
        ORDER BY e.match_score DESC
    """)

    result = db.execute(query, {"job_id": job_id})
    rows = result.fetchall()

    applicants = []
    for row in rows:
        applicants.append({
            "evaluation_id": row[0],
            "applicant_id": row[1],
            "applicant_name": row[2],
            "overall_score": round(row[3], 1) if row[3] else 0,
            "normalized_score": round(row[4], 1) if row[4] else None,
            "created_at": row[5].isoformat() if row[5] else None
        })

    return {
        "job_id": job_id,
        "applicants": applicants,
        "total_count": len(applicants)
    }


@router.get("/jobs/{job_id}/applicants/{applicant_id}/result")
async def get_applicant_detail(
    job_id: int,
    applicant_id: int,
    db: Session = Depends(get_db)
):
    """지원자 상세 평가 결과"""
    logger.info(f"Getting applicant detail for job ID: {job_id}, applicant ID: {applicant_id}")
    # Raw SQL로 조회
    query = text("""
        SELECT
            e.id,
            e.applicant_id,
            a.name,
            e.match_score,
            e.normalized_score,
            e.confidence_score,
            e.competency_scores,
            e.reasoning_log,
            e.aggregated_evaluation,
            e.match_result,
            e.created_at
        FROM evaluations e
        JOIN applicants a ON e.applicant_id = a.id
        WHERE e.job_id = :job_id AND e.applicant_id = :applicant_id
        LIMIT 1
    """)

    result = db.execute(query, {"job_id": job_id, "applicant_id": applicant_id})
    row = result.fetchone()

    if not row:
        raise HTTPException(
            status_code=404,
            detail=f"Evaluation not found for job_id={job_id}, applicant_id={applicant_id}"
        )

    return {
        "evaluation_id": row[0],
        "applicant_id": row[1],
        "applicant_name": row[2],
        "overall_score": round(row[3], 1) if row[3] else 0,
        "normalized_score": round(row[4], 1) if row[4] else None,
        "confidence_score": round(row[5], 2) if row[5] else None,
        "competency_scores": row[6],
        "reasoning_log": row[7],
        "aggregated_evaluation": row[8],
        "match_result": row[9],
        "created_at": row[10].isoformat() if row[10] else None
    }


@router.get("/jobs/{job_id}/statistics")
async def get_job_statistics(
    job_id: int,
    db: Session = Depends(get_db)
):
    """Job별 통계"""
    logger.info(f"Getting job statistics for job ID: {job_id}")
    query = text("""
        SELECT
            COUNT(*) as total,
            AVG(match_score) as avg_score,
            MIN(match_score) as min_score,
            MAX(match_score) as max_score
        FROM evaluations
        WHERE job_id = :job_id
    """)

    result = db.execute(query, {"job_id": job_id})
    row = result.fetchone()

    if not row or row[0] == 0:
        return {
            "job_id": job_id,
            "total_evaluations": 0,
            "average_score": 0,
            "median_score": 0,
            "min_score": 0,
            "max_score": 0
        }

    # 중간값 계산
    median_query = text("""
        SELECT match_score
        FROM evaluations
        WHERE job_id = :job_id
        ORDER BY match_score
        LIMIT 1 OFFSET :offset
    """)

    offset = row[0] // 2
    median_result = db.execute(median_query, {"job_id": job_id, "offset": offset})
    median_row = median_result.fetchone()

    return {
        "job_id": job_id,
        "total_evaluations": row[0],
        "average_score": round(row[1], 2) if row[1] else 0,
        "median_score": round(median_row[0], 2) if median_row else 0,
        "min_score": round(row[2], 1) if row[2] else 0,
        "max_score": round(row[3], 1) if row[3] else 0
    }
