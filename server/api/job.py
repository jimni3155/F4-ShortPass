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
