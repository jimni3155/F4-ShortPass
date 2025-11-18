# server/api/job.py
"""
Job 관련 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List

from db.database import get_db
from services.job_service import JobService
from pydantic import BaseModel


router = APIRouter(prefix="/jobs", tags=["jobs"])


# Response Models
class JobResponse(BaseModel):
    job_id: int
    company_id: int
    title: str
    created_at: str
    total_chunks: int

    class Config:
        from_attributes = True


class ChunkResponse(BaseModel):
    chunk_id: int
    chunk_text: str
    chunk_index: int
    has_embedding: bool


class JobDetailResponse(BaseModel):
    job_id: int
    company_id: int
    title: str
    description: str
    created_at: str
    chunks: List[ChunkResponse]
    total_chunks: int


class SearchResult(BaseModel):
    chunk_id: int
    job_id: int
    chunk_text: str
    chunk_index: int
    similarity: float


# Endpoints
@router.post("/upload", response_model=JobResponse)
async def upload_jd_pdf(
    pdf_file: UploadFile = File(..., description="JD PDF 파일"),
    company_id: int = Form(..., description="회사 ID"),
    title: str = Form(..., description="채용 공고 제목"),
    db: Session = Depends(get_db)
):
    """
    JD PDF 업로드 및 처리

    전체 플로우:
    1. PDF 파일 업로드 받기
    2. S3에 저장
    3. PDF 파싱 및 텍스트 추출
    4. 청크 분할
    5. Bedrock Titan으로 임베딩 생성
    6. DB에 저장 (jobs, job_chunks)

    Args:
        pdf_file: PDF 파일
        company_id: 회사 ID
        title: 채용 공고 제목

    Returns:
        JobResponse: 생성된 Job 정보
    """
    # PDF 파일 검증
    if not pdf_file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    # 파일 크기 제한 (예: 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    pdf_content = await pdf_file.read()

    if len(pdf_content) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum limit of {max_size / (1024*1024)}MB"
        )

    # Job 서비스로 처리
    try:
        job_service = JobService()
        job = await job_service.process_jd_pdf(
            db=db,
            pdf_content=pdf_content,
            file_name=pdf_file.filename,
            company_id=company_id,
            title=title
        )

        # 청크 개수 조회
        chunk_count = len(job.chunks)

        return JobResponse(
            job_id=job.id,
            company_id=job.company_id,
            title=job.title,
            created_at=job.created_at.isoformat(),
            total_chunks=chunk_count
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process JD PDF: {str(e)}"
        )


@router.get("/{job_id}", response_model=JobDetailResponse)
async def get_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Job 상세 정보 조회 (청크 포함)

    Args:
        job_id: Job ID

    Returns:
        JobDetailResponse: Job 상세 정보
    """
    job_service = JobService()
    job_data = job_service.get_job_with_chunks(db, job_id)

    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobDetailResponse(
        job_id=job_data["job_id"],
        company_id=job_data["company_id"],
        title=job_data["title"],
        description=job_data["description"],
        created_at=job_data["created_at"].isoformat(),
        chunks=[
            ChunkResponse(
                chunk_id=chunk["chunk_id"],
                chunk_text=chunk["chunk_text"],
                chunk_index=chunk["chunk_index"],
                has_embedding=chunk["has_embedding"]
            )
            for chunk in job_data["chunks"]
        ],
        total_chunks=job_data["total_chunks"]
    )


@router.post("/search", response_model=List[SearchResult])
async def search_similar_chunks(
    query: str = Form(..., description="검색 쿼리"),
    top_k: int = Form(5, description="반환할 결과 개수"),
    job_id: Optional[int] = Form(None, description="특정 Job으로 제한"),
    db: Session = Depends(get_db)
):
    """
    벡터 유사도 기반 청크 검색

    Args:
        query: 검색 쿼리 텍스트
        top_k: 반환할 상위 결과 개수
        job_id: 특정 Job으로 제한 (선택)

    Returns:
        List[SearchResult]: 유사한 청크 리스트
    """
    try:
        job_service = JobService()
        results = job_service.search_similar_chunks(
            db=db,
            query_text=query,
            top_k=top_k,
            job_id=job_id
        )

        return [
            SearchResult(
                chunk_id=r["chunk_id"],
                job_id=r["job_id"],
                chunk_text=r["chunk_text"],
                chunk_index=r["chunk_index"],
                similarity=r["similarity"]
            )
            for r in results
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@router.delete("/{job_id}")
async def delete_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Job 삭제 (청크도 함께 삭제됨)

    Args:
        job_id: Job ID

    Returns:
        Dict: 삭제 결과
    """
    job_service = JobService()
    success = job_service.delete_job(db, job_id)

    if not success:
        raise HTTPException(status_code=404, detail="Job not found")

    return {"message": f"Job {job_id} deleted successfully"}


class CompetencyAnalysisResponse(BaseModel):
    """핵심 역량 분석 결과"""
    competencies: List[dict]
    category_weights: dict
    reasoning: str

    class Config:
        from_attributes = True


@router.post("/analyze-competencies", response_model=CompetencyAnalysisResponse)
async def analyze_jd_competencies(
    pdf_file: UploadFile = File(..., description="JD PDF 파일"),
    company_id: int = Form(..., description="회사 ID"),
    company_url: Optional[str] = Form(None, description="회사 URL (핵심 가치 분석용)"),
    db: Session = Depends(get_db)
):
    """
    JD PDF에서 핵심 역량 분석

    전체 플로우:
    1. PDF 파일 읽기 및 파싱
    2. JD 텍스트에서 핵심 역량 추출
    3. (선택) company_url이 있으면 RAG로 회사 가치 검색
    4. 역량 분석 결과 반환

    Args:
        pdf_file: JD PDF 파일
        company_id: 회사 ID
        company_url: 회사 소개 URL (선택)

    Returns:
        CompetencyAnalysisResponse: 역량 분석 결과
    """
    # PDF 파일 검증
    if not pdf_file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    # 파일 크기 제한 (10MB)
    max_size = 10 * 1024 * 1024
    pdf_content = await pdf_file.read()

    if len(pdf_content) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum limit of {max_size / (1024*1024)}MB"
        )

    try:
        print(f"\n{'='*60}")
        print(f"[analyze_jd_competencies] Starting JD competency analysis")
        print(f"{'='*60}")
        print(f"  - Company ID: {company_id}")
        print(f"  - Company URL: {company_url or 'Not provided'}")
        print(f"  - PDF file: {pdf_file.filename}")

        job_service = JobService()

        # 1. PDF 파싱
        print("\n[Step 1/3] Parsing PDF...")
        from ai.parsers.jd_parser import JDParser
        jd_parser = JDParser()

        try:
            parsed_result = jd_parser.parse_and_chunk(pdf_content=pdf_content)
            full_text = parsed_result["full_text"]
            print(f"  ✓ PDF parsed: {len(full_text)} characters")
        except Exception as e:
            print(f"  ✗ PDF parsing failed: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse PDF: {str(e)}"
            )

        # 2. 핵심 역량 추출
        print(f"\n[Step 2/3] Extracting competencies from JD...")

        try:
            analysis_result = await job_service._extract_company_weights(full_text)
        except Exception as e:
            print(f"  ✗ Competency extraction failed: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to extract competencies: {str(e)}"
            )

        if not analysis_result:
            print(f"  ✗ No analysis result returned")
            raise HTTPException(
                status_code=500,
                detail="Failed to analyze competencies - no result returned"
            )

        print(f"  ✓ Competencies extracted: {len(analysis_result.get('competencies', []))} competencies")

        # 3. (선택) Company URL이 있으면 DB에 업데이트
        print(f"\n[Step 3/3] Updating company information...")
        if company_url:
            try:
                from models.interview import Company
                company = db.query(Company).filter(Company.id == company_id).first()
                if company:
                    company.company_url = company_url
                    db.commit()
                    print(f"  ✓ Company URL updated")
                else:
                    print(f"  ⚠ Company {company_id} not found")
            except Exception as e:
                print(f"  ⚠ Failed to update company URL: {e}")
                # Continue without failing the entire request
        else:
            print(f"  - No company URL to update")

        print(f"\n{'='*60}")
        print(f"✓ Analysis completed successfully!")
        print(f"  - Competencies found: {len(analysis_result.get('competencies', []))}")
        print(f"{'='*60}\n")

        return CompetencyAnalysisResponse(
            competencies=analysis_result.get("competencies", []),
            category_weights=analysis_result.get("weights", {}),
            reasoning=analysis_result.get("reasoning", "")
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"✗ Competency analysis failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        print(f"{'='*60}\n")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze competencies: {str(e)}"
        )
