# server/api/persona.py
"""
페르소나 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from db.database import get_db
from services.persona_service import PersonaService
from schemas.persona import (
    PersonaResponse,
    PersonaListResponse,
    QuestionResponse,
    PersonaUploadResponse
)
import logging


router = APIRouter()
logger = logging.getLogger("uvicorn")


@router.post("/upload", response_model=PersonaUploadResponse, status_code=201)
async def upload_persona_pdf(
    company_id: int = Form(..., description="회사 ID"),
    pdf_file: UploadFile = File(..., description="페르소나 질문 PDF 파일"),
    db: Session = Depends(get_db)
):
    """
    페르소나 PDF 업로드

    PDF 파일에서 질문을 추출하고 페르소나를 생성합니다.

    Args:
        company_id: 회사 ID
        pdf_file: PDF 파일

    Returns:
        PersonaUploadResponse: 생성된 페르소나와 질문 리스트
    """
    logger.info(f"Uploading persona PDF for company ID: {company_id}")
    # 1. 파일 유효성 검사
    if not pdf_file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="PDF 파일만 업로드 가능합니다"
        )

    # 파일 크기 체크 (10MB)
    content = await pdf_file.read()
    file_size = len(content)
    max_size = 10 * 1024 * 1024  # 10MB

    if file_size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"파일 크기는 10MB를 초과할 수 없습니다 (현재: {file_size / 1024 / 1024:.2f}MB)"
        )

    # 2. 페르소나 생성
    try:
        service = PersonaService(db)
        result = service.create_persona_from_pdf(
            company_id=company_id,
            pdf_file_content=content,
            pdf_file_name=pdf_file.filename
        )

        persona = result["persona"]
        questions = result["questions"]

        return PersonaUploadResponse(
            persona=PersonaResponse.model_validate(persona),
            questions=[QuestionResponse.model_validate(q) for q in questions],
            message=f"페르소나 생성 완료: {len(questions)}개의 질문이 추출되었습니다"
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"❌ 페르소나 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=f"페르소나 생성 실패: {str(e)}")


@router.get("/{persona_id}", response_model=PersonaResponse)
async def get_persona(
    persona_id: int,
    db: Session = Depends(get_db)
):
    """
    페르소나 상세 조회

    Args:
        persona_id: 페르소나 ID

    Returns:
        PersonaResponse: 페르소나 정보
    """
    logger.info(f"Getting persona with ID: {persona_id}")
    service = PersonaService(db)
    persona = service.get_persona(persona_id)

    if not persona:
        raise HTTPException(status_code=404, detail="페르소나를 찾을 수 없습니다")

    return PersonaResponse.model_validate(persona)


@router.get("/{persona_id}/questions", response_model=List[QuestionResponse])
async def get_persona_questions(
    persona_id: int,
    db: Session = Depends(get_db)
):
    """
    페르소나의 질문 목록 조회

    Args:
        persona_id: 페르소나 ID

    Returns:
        List[QuestionResponse]: 질문 리스트
    """
    logger.info(f"Getting questions for persona ID: {persona_id}")
    service = PersonaService(db)

    # 페르소나 존재 확인
    persona = service.get_persona(persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="페르소나를 찾을 수 없습니다")

    questions = service.get_persona_questions(persona_id)

    return [QuestionResponse.model_validate(q) for q in questions]


@router.get("/company/{company_id}", response_model=PersonaListResponse)
async def get_personas_by_company(
    company_id: int,
    db: Session = Depends(get_db)
):
    """
    회사별 페르소나 목록 조회

    Args:
        company_id: 회사 ID

    Returns:
        PersonaListResponse: 페르소나 리스트
    """
    logger.info(f"Getting personas for company ID: {company_id}")
    service = PersonaService(db)
    personas = service.get_personas_by_company(company_id)

    return PersonaListResponse(
        personas=[PersonaResponse.model_validate(p) for p in personas],
        total=len(personas)
    )


@router.get("/", response_model=PersonaListResponse)
async def get_all_personas(
    db: Session = Depends(get_db)
):
    """
    전체 페르소나 목록 조회

    Returns:
        PersonaListResponse: 페르소나 리스트
    """
    logger.info("Getting all personas")
    service = PersonaService(db)
    personas = service.get_all_personas()

    return PersonaListResponse(
        personas=[PersonaResponse.model_validate(p) for p in personas],
        total=len(personas)
    )


@router.delete("/{persona_id}", status_code=204)
async def delete_persona(
    persona_id: int,
    db: Session = Depends(get_db)
):
    """
    페르소나 삭제

    Args:
        persona_id: 페르소나 ID
    """
    logger.info(f"Deleting persona with ID: {persona_id}")
    service = PersonaService(db)
    success = service.delete_persona(persona_id)

    if not success:
        raise HTTPException(status_code=404, detail="페르소나를 찾을 수 없습니다")

    return None
