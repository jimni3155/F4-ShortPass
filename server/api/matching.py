# app/api/v1/endpoints/matching.py
"""
매칭 결과 조회 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from services.matching_service import MatchingService
from schemas.matching import CompanyMatchResult, ApplicantMatchResult
from ai.scorers.score_aggregator import ScoreAggregator
from ai.scorers.matching_scorer import MatchingScorer

router = APIRouter()


@router.get(
    "/applicant/interviews/{interview_id}",
    response_model=CompanyMatchResult,
    summary="지원자 매칭 결과 조회",
    description="면접 완료 후 지원자가 선택한 기업들과의 매칭 점수 및 순위 조회"
)
async def get_applicant_matching_result(
    interview_id: int,
    db: Session = Depends(get_db)
):
    """
    지원자가 보는 매칭 결과
    
    - 면접 세션 ID로 조회
    - 선택한 1~3개 기업과의 매칭 점수
    - 순위순으로 정렬되어 반환
    
    Example Response:
    {
        "applicant_id": 1,
        "applicant_name": "김개발",
        "interview_session_id": 1,
        "interview_completed_at": "2025-01-15T10:00:00",
        "matches": [
            {
                "rank": 1,
                "company_id": 101,
                "company_name": "테크스타트업A",
                "job_title": "백엔드 개발자",
                "match_score": {
                    "total_score": 87.5,
                    "technical_score": 90.0,
                    "cultural_score": 85.0,
                    "experience_score": 88.0,
                    "soft_skills_score": 87.0,
                    "strengths": ["기술력 우수", "문화 적합도 높음"],
                    "weaknesses": ["일부 우대 기술 부족"]
                }
            },
            ...
        ]
    }
    """
    # 서비스 초기화
    score_aggregator = ScoreAggregator()
    matching_scorer = MatchingScorer()
    matching_service = MatchingService(
        db=db,
        score_aggregator=score_aggregator,
        matching_scorer=matching_scorer
    )
    
    try:
        result = await matching_service.calculate_applicant_matches(interview_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"매칭 계산 실패: {str(e)}")


@router.get(
    "/company/jobs/{job_id}",
    response_model=ApplicantMatchResult,
    summary="기업 매칭 결과 조회",
    description="특정 채용 공고에 지원한 지원자들의 매칭 점수 및 순위 조회"
)
async def get_company_matching_result(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    기업이 보는 매칭 결과
    
    - Job ID로 조회
    - 해당 공고에 지원한 모든 지원자
    - 매칭 점수 순위순으로 정렬
    - Blind 모드 적용
    
    Example Response:
    {
        "company_id": 1,
        "company_name": "테크스타트업",
        "job_id": 101,
        "applicants": [
            {
                "rank": 1,
                "applicant_id": 1,
                "applicant_name": "지원자_001",  // Blind 시
                "age": null,  // Blind 시
                "education": null,  // Blind 시
                "gender": null,  // Blind 시
                "match_score": {
                    "total_score": 88.5,
                    "technical_score": 92.0,
                    "cultural_score": 86.0,
                    "experience_score": 87.0,
                    "soft_skills_score": 89.0,
                    "strengths": ["기술 역량 탁월", "협업 능력 우수"],
                    "weaknesses": []
                },
                "interview_summary": "기술력과 문화 적합도 모두 뛰어남",
                "highlights": ["Python 전문가", "스타트업 경험", "리더십"]
            },
            ...
        ],
        "total_applicants": 15
    }
    """
    # 서비스 초기화
    score_aggregator = ScoreAggregator()
    matching_scorer = MatchingScorer()
    matching_service = MatchingService(
        db=db,
        score_aggregator=score_aggregator,
        matching_scorer=matching_scorer
    )
    
    try:
        result = await matching_service.calculate_company_matches(job_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"매칭 계산 실패: {str(e)}")


@router.get(
    "/applicant/{applicant_id}/summary",
    summary="지원자 매칭 요약",
    description="지원자의 간단한 매칭 요약 (대시보드용)"
)
async def get_applicant_summary(
    applicant_id: int,
    db: Session = Depends(get_db)
):
    """
    지원자 대시보드용 요약 정보
    
    - 최근 면접 결과
    - Top 3 매칭 기업
    - 전체 평균 점수
    """
    # TODO: 구현
    return {
        "applicant_id": applicant_id,
        "recent_interview": {
            "interview_id": 1,
            "completed_at": "2025-01-15T10:00:00",
            "companies_count": 3
        },
        "top_matches": [
            {"company_name": "테크스타트업A", "score": 87.5},
            {"company_name": "AI기업B", "score": 85.0},
            {"company_name": "핀테크C", "score": 82.3}
        ],
        "average_score": 84.9
    }