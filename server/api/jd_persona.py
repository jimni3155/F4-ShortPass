# server/api/jd_persona.py
"""
JD 기반 페르소나 생성 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import logging
import json

from db.database import get_db
from services.competency_service import CompetencyService
from services.job_service import JobService
from services.jd_persona_service import JDPersonaService
from ai.parsers.jd_parser import JDParser


router = APIRouter(prefix="/jd-persona", tags=["JD Persona"])
logger = logging.getLogger("uvicorn")


# Request/Response Models
class CompetencyAnalysisResponse(BaseModel):
    """역량 분석 결과"""
    job_id: int
    common_competencies: List[str]
    job_competencies: List[str]
    analysis_summary: str
    visualization_data: Dict[str, Any]


class PersonaRequest(BaseModel):
    """페르소나 생성 요청"""
    job_id: int
    company_questions: List[str]  # 기업 필수 질문 3개


class PersonaResponse(BaseModel):
    """페르소나 생성 결과"""
    job_id: int
    company: str
    common_competencies: List[str]
    job_competencies: List[str]
    core_questions: List[str]
    persona_summary: List[Dict[str, Any]]
    created_at: str


# Endpoints
@router.post("/upload", response_model=CompetencyAnalysisResponse)
async def upload_jd_and_analyze(
    pdf_file: UploadFile = File(..., description="JD PDF 파일"),
    company_id: int = Form(..., description="회사 ID"),
    title: str = Form(..., description="채용 공고 제목"),
    company_url: str = Form(None, description="기업 웹사이트 URL (선택)"),
    db: Session = Depends(get_db)
):
    """
    JD PDF 업로드 및 역량 분석

    플로우:
    1. PDF 업로드 및 텍스트 추출
    2. 공통/직무 역량 자동 분류
    3. 시각화 데이터 생성

    Args:
        pdf_file: JD PDF 파일
        company_id: 회사 ID
        title: 채용 공고 제목

    Returns:
        CompetencyAnalysisResponse: 역량 분석 결과
    """
    logger.info(f"Uploading JD for company ID: {company_id}, title: {title}")
    try:
        # PDF 파일 검증
        if not pdf_file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed"
            )

        # 파일 크기 제한 (10MB)
        pdf_content = await pdf_file.read()
        max_size = 10 * 1024 * 1024

        if len(pdf_content) > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum limit of {max_size / (1024*1024)}MB"
            )

        print(f"\n Starting JD upload and analysis: {pdf_file.filename}")

        # ===== MOCK MODE =====
        # PDF 업로드는 받지만, 실제로는 미리 정의된 데이터 반환
        # companyId=1 (삼성물산 패션부문), jobId=1 (상품기획/Retail영업)

        # Mock 데이터 (DB 조회 없이 hardcoded)
        mock_job_id = 1
        # CompetencyService.COMMON_COMPETENCIES 사용
        from services.competency_service import CompetencyService
        common_competencies = CompetencyService.COMMON_COMPETENCIES
        job_competencies = [
            "매출·트렌드 데이터 분석 및 상품 기획 (MD 프로세스)",
            "시즌 전략 수립 및 비즈니스 문제해결 (KPI 관리)",
            "소싱·생산·유통 밸류체인 최적화 (원가·마진 관리)",
            "고객 여정 설계 및 VMD·마케팅 통합 전략",
            "유관부서 협업 및 이해관계자 협상 (디자인/생산/영업)"
        ]

        print(f"✅ Mock 데이터 사용: Job ID={mock_job_id}, 역량 {len(job_competencies)}개")

        # 시각화 데이터 생성
        competency_service = CompetencyService()
        visualization_data = competency_service.get_competency_visualization_data(
            job_competencies=job_competencies
        )

        return CompetencyAnalysisResponse(
            job_id=mock_job_id,
            common_competencies=common_competencies,
            job_competencies=job_competencies,
            analysis_summary="삼성물산 패션부문 MD/영업 직무 핵심 역량 분석 완료 (Mock)",
            visualization_data=visualization_data
        )

    except Exception as e:
        print(f"❌ Failed to process JD upload: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process JD upload: {str(e)}"
        )


@router.post("/generate-persona", response_model=PersonaResponse)
async def generate_persona(
    request: PersonaRequest,
    db: Session = Depends(get_db)
):
    """
    페르소나 생성

    플로우:
    1. Job ID로 JD 텍스트 조회
    2. 기업 필수 질문과 함께 LLM에 페르소나 생성 요청
    3. 결과 반환

    Args:
        request: 페르소나 생성 요청 데이터

    Returns:
        PersonaResponse: 생성된 페르소나 정보
    """
    logger.info(f"Generating persona for job ID: {request.job_id}")
    try:
        print(f"\n🎭 Starting persona generation for Job ID: {request.job_id}")

        # ===== MOCK MODE =====
        # 페르소나 생성 요청을 받지만, 미리 정의된 데이터 반환

        # 기업 질문 검증
        if len(request.company_questions) != 3:
            raise HTTPException(
                status_code=400,
                detail="Exactly 3 company questions are required"
            )

        print(f"❓ Company questions received: {request.company_questions}")

        # Mock 페르소나 데이터
        from datetime import datetime
        from services.competency_service import CompetencyService

        mock_company_name = "삼성물산 패션부문"
        # CompetencyService.COMMON_COMPETENCIES 사용 (6개)
        mock_common_competencies = CompetencyService.COMMON_COMPETENCIES
        mock_job_competencies = [
            "매출·트렌드 데이터 분석 및 상품 기획 (MD 프로세스)",
            "시즌 전략 수립 및 비즈니스 문제해결 (KPI 관리)",
            "소싱·생산·유통 밸류체인 최적화 (원가·마진 관리)",
            "고객 여정 설계 및 VMD·마케팅 통합 전략",
            "유관부서 협업 및 이해관계자 협상 (디자인/생산/영업)"
        ]

        # 사용자가 입력한 3개 질문 사용
        mock_core_questions = request.company_questions

        mock_persona_summary = [
            {
                "type": "전략적 사고형 면접관",
                "focus": "시장 분석 및 데이터 기반 의사결정 능력 평가",
                "style": "논리적이고 분석적, 구체적인 근거를 요구",
                "target_competencies": ["매출·트렌드 데이터 분석 및 상품 기획 (MD 프로세스)", "시즌 전략 수립 및 비즈니스 문제해결 (KPI 관리)"]
            },
            {
                "type": "실행력 중심형 면접관",
                "focus": "목표 달성을 위한 창의적 실행과 협업 능력 평가",
                "style": "실무 경험과 구체적 성과를 중시",
                "target_competencies": ["고객 여정 설계 및 VMD·마케팅 통합 전략", "유관부서 협업 및 이해관계자 협상 (디자인/생산/영업)"]
            },
            {
                "type": "글로벌 비즈니스형 면접관",
                "focus": "글로벌 감각과 비즈니스 마인드 평가",
                "style": "전략적 사고와 글로벌 시각을 평가",
                "target_competencies": ["소싱·생산·유통 밸류체인 최적화 (원가·마진 관리)"]
            }
        ]

        print(f"✅ Mock 페르소나 데이터 생성 완료")

        return PersonaResponse(
            job_id=request.job_id,
            company=mock_company_name,
            common_competencies=mock_common_competencies,
            job_competencies=mock_job_competencies,
            core_questions=mock_core_questions,
            persona_summary=mock_persona_summary,
            created_at=datetime.now().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to generate persona: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate persona: {str(e)}"
        )


@router.get("/analysis/{job_id}", response_model=CompetencyAnalysisResponse)
async def get_competency_analysis(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    기존 Job의 역량 분석 조회

    Args:
        job_id: Job ID

    Returns:
        CompetencyAnalysisResponse: 역량 분석 결과
    """
    logger.info(f"Getting competency analysis for job ID: {job_id}")
    try:
        # Job 조회
        job_service = JobService()
        job_data = job_service.get_job_with_chunks(db, job_id)

        if not job_data:
            raise HTTPException(
                status_code=404,
                detail="Job not found"
            )

        # 역량 분석 (재실행)
        competency_service = CompetencyService()
        competency_data = await competency_service.analyze_jd_competencies(
            jd_text=job_data["description"]
        )

        # 시각화 데이터 생성
        visualization_data = competency_service.get_competency_visualization_data(
            job_competencies=competency_data["job_competencies"]
        )

        return CompetencyAnalysisResponse(
            job_id=job_id,
            common_competencies=competency_data["common_competencies"],
            job_competencies=competency_data["job_competencies"],
            analysis_summary=competency_data.get("analysis_summary", ""),
            visualization_data=visualization_data
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to get competency analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get competency analysis: {str(e)}"
        )


@router.get("/jobs/{job_id}/basic-info")
async def get_job_basic_info(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Job 기본 정보 조회 (제목, 회사 등)

    Args:
        job_id: Job ID

    Returns:
        Dict: Job 기본 정보
    """
    logger.info(f"Getting basic info for job ID: {job_id}")
    try:
        job_service = JobService()
        job_data = job_service.get_job_with_chunks(db, job_id)

        if not job_data:
            raise HTTPException(
                status_code=404,
                detail="Job not found"
            )

        return {
            "job_id": job_data["job_id"],
            "company_id": job_data["company_id"],
            "title": job_data["title"],
            "created_at": job_data["created_at"].isoformat(),
            "total_chunks": job_data["total_chunks"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get job info: {str(e)}"
        )


@router.get("/test/sample-competencies")
async def get_sample_competencies():
    """
    테스트용 샘플 역량 데이터
    """
    logger.info("Getting sample competencies")
    competency_service = CompetencyService()

    sample_job_competencies = [
        "데이터분석", "문제해결력", "창의적 사고",
        "기술적 이해", "리더십", "커뮤니케이션"
    ]

    return {
        "common_competencies": competency_service.COMMON_COMPETENCIES,
        "job_competencies": sample_job_competencies,
        "visualization_data": competency_service.get_competency_visualization_data(
            sample_job_competencies
        )
    }