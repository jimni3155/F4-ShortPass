# server/api/jd_persona.py
"""
JD 기반 페르소나 생성 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from db.database import get_db
from services.competency_service import CompetencyService
from services.job_service import JobService
from services.jd_persona_service import JDPersonaService
from ai.parsers.jd_parser import JDParser


router = APIRouter(prefix="/jd-persona", tags=["JD Persona"])


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

        print(f"\n🚀 Starting JD upload and analysis: {pdf_file.filename}")

        # 1. 기존 Job 서비스로 PDF 처리 (S3 업로드, 청킹, 임베딩)
        job_service = JobService()
        job = await job_service.process_jd_pdf(
            db=db,
            pdf_content=pdf_content,
            file_name=pdf_file.filename,
            company_id=company_id,
            title=title
        )

        print(f"✅ Job created with ID: {job.id}")

        # 2. 역량 분석
        competency_service = CompetencyService()
        competency_data = await competency_service.analyze_jd_competencies(
            jd_text=job.description
        )

        print(f"✅ Competencies analyzed: {len(competency_data['job_competencies'])} job competencies")

        # 3. 시각화 데이터 생성
        visualization_data = competency_service.get_competency_visualization_data(
            job_competencies=competency_data["job_competencies"]
        )

        return CompetencyAnalysisResponse(
            job_id=job.id,
            common_competencies=competency_data["common_competencies"],
            job_competencies=competency_data["job_competencies"],
            analysis_summary=competency_data.get("analysis_summary", ""),
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
    try:
        print(f"\n🎭 Starting persona generation for Job ID: {request.job_id}")

        # 1. Job 정보 조회
        job_service = JobService()
        job_data = job_service.get_job_with_chunks(db, request.job_id)

        if not job_data:
            raise HTTPException(
                status_code=404,
                detail="Job not found"
            )

        jd_text = job_data["description"]

        # 2. 역량 재분석 (이미 분석된 데이터가 있다면 캐시 활용 가능)
        competency_service = CompetencyService()
        competency_data = await competency_service.analyze_jd_competencies(jd_text)

        print(f"📊 Competencies: {competency_data['job_competencies']}")

        # 3. 기업 질문 검증
        if len(request.company_questions) != 3:
            raise HTTPException(
                status_code=400,
                detail="Exactly 3 company questions are required"
            )

        print(f"❓ Company questions: {len(request.company_questions)} questions received")

        # 4. 페르소나 생성 및 DB 저장
        persona_service = JDPersonaService()
        result = await persona_service.create_and_save_persona(
            db=db,
            job_id=request.job_id,
            company_id=job_data["company_id"],
            jd_text=jd_text,
            company_questions=request.company_questions
        )

        print(f"🎭 Generated and saved persona with ID: {result.get('id')}")

        return PersonaResponse(
            job_id=request.job_id,
            company=result["company_name"],
            common_competencies=result["common_competencies"],
            job_competencies=result["job_competencies"],
            core_questions=result["core_questions"],
            persona_summary=result["persona_summary"],
            created_at=result["created_at"]
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