# server/api/applicant.py
"""
Applicant 관련 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List

from db.database import get_db
from services.applicant_service import ApplicantService
from schemas.applicant import (
    ApplicantCreate,
    ApplicantResponse,
    ApplicantDetailResponse,
    ApplicantUpdate
)


router = APIRouter(prefix="/applicants", tags=["applicants"])


@router.post("/", response_model=ApplicantResponse)
async def create_applicant(
    name: str = Form(..., description="이름"),
    email: str = Form(..., description="이메일"),
    gender: Optional[str] = Form(None, description="성별"),
    education: Optional[str] = Form(None, description="학력"),
    birthdate: Optional[str] = Form(None, description="생년월일 (YYYY-MM-DD)"),
    portfolio_file: Optional[UploadFile] = File(None, description="포트폴리오 PDF"),
    db: Session = Depends(get_db)
):
    """
    지원자 생성 또는 업데이트 (Upsert)

    동일한 이메일이 이미 존재하면 기존 지원자 정보를 업데이트합니다.

    전체 플로우:
    1. 이메일로 기존 지원자 확인
    2. 존재하면 업데이트, 없으면 새로 생성
    3. 포트폴리오 PDF가 있으면 S3에 업로드
    4. DB에 파일 경로 저장

    Args:
        name: 이름
        email: 이메일
        gender: 성별
        education: 학력
        birthdate: 생년월일
        portfolio_file: 포트폴리오 PDF
        db: Database session

    Returns:
        ApplicantResponse: 생성 또는 업데이트된 지원자 정보
    """
    try:
        applicant_service = ApplicantService()

        # 지원자 생성
        applicant = applicant_service.create_applicant(
            db=db,
            name=name,
            email=email,
            gender=gender,
            education=education,
            birthdate=birthdate,
        )

        # 포트폴리오 업로드 (옵션)
        if portfolio_file and portfolio_file.filename:
            # PDF 파일 검증
            if not portfolio_file.filename.endswith('.pdf'):
                raise HTTPException(
                    status_code=400,
                    detail="Only PDF files are allowed for portfolio"
                )

            # 파일 크기 제한 (10MB)
            max_size = 10 * 1024 * 1024
            file_content = await portfolio_file.read()

            if len(file_content) > max_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"File size exceeds maximum limit of {max_size / (1024*1024)}MB"
                )

            # S3 업로드
            applicant_service.upload_portfolio(
                db=db,
                applicant_id=applicant.id,
                file_content=file_content,
                file_name=portfolio_file.filename
            )

        return ApplicantResponse.model_validate(applicant)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create applicant: {str(e)}"
        )


@router.get("/{applicant_id}", response_model=ApplicantDetailResponse)
async def get_applicant(
    applicant_id: int,
    db: Session = Depends(get_db)
):
    """
    지원자 상세 정보 조회

    Args:
        applicant_id: 지원자 ID
        db: Database session

    Returns:
        ApplicantDetailResponse: 지원자 상세 정보
    """
    applicant_service = ApplicantService()
    applicant = applicant_service.get_applicant(db, applicant_id)

    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")

    return ApplicantDetailResponse.model_validate(applicant)


@router.get("/", response_model=List[ApplicantResponse])
async def get_applicants(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    지원자 목록 조회

    Args:
        skip: 건너뛸 개수
        limit: 조회할 개수
        db: Database session

    Returns:
        List[ApplicantResponse]: 지원자 목록
    """
    applicant_service = ApplicantService()
    applicants = applicant_service.get_applicants(db, skip=skip, limit=limit)

    return [ApplicantResponse.model_validate(a) for a in applicants]


@router.patch("/{applicant_id}", response_model=ApplicantResponse)
async def update_applicant(
    applicant_id: int,
    applicant_update: ApplicantUpdate,
    db: Session = Depends(get_db)
):
    """
    지원자 정보 수정

    Args:
        applicant_id: 지원자 ID
        applicant_update: 수정할 정보
        db: Database session

    Returns:
        ApplicantResponse: 수정된 지원자 정보
    """
    applicant_service = ApplicantService()

    update_data = applicant_update.model_dump(exclude_unset=True)
    applicant = applicant_service.update_applicant(
        db=db,
        applicant_id=applicant_id,
        **update_data
    )

    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")

    return ApplicantResponse.model_validate(applicant)


@router.delete("/{applicant_id}")
async def delete_applicant(
    applicant_id: int,
    db: Session = Depends(get_db)
):
    """
    지원자 삭제

    Args:
        applicant_id: 지원자 ID
        db: Database session

    Returns:
        dict: 삭제 결과
    """
    applicant_service = ApplicantService()
    success = applicant_service.delete_applicant(db, applicant_id)

    if not success:
        raise HTTPException(status_code=404, detail="Applicant not found")

    return {"message": f"Applicant {applicant_id} deleted successfully"}
