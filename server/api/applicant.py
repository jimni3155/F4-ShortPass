# server/api/applicant.py
"""
Applicant 관련 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List
import logging

from db.database import get_db
from services.applicant_service import ApplicantService
from schemas.applicant import (
    ApplicantCreate,
    ApplicantResponse,
    ApplicantDetailResponse,
    ApplicantUpdate
)
from schemas.evaluation import EvaluationDetailResponse


# Mock data, converted from the frontend mock file
candidate_detail_mock = {
  "candidate_id": "CAND_001",
  "name": "김지원",
  "job_title": "상품기획(MD) / Retail영업",
  "total_score": 92,
  "grade": "S",
  "ai_summary": "김지원 지원자는 Data-Driven Insight(95점)와 Strategic Problem Solving(90점) 역량이 매우 뛰어납니다. 특히 매출 하락 원인을 분석할 때 외부 시장 데이터와 내부 CRM 데이터를 결합하여 논리를 전개한 점이 컨설턴트 수준의 사고력으로 평가되었습니다. 다만, 글로벌 파트너와의 협상 경험(Global Mindset)은 검증이 더 필요합니다.",
  "radar_chart_data": {
    "labels": ["Data Insight", "Strategic Solving", "Value Chain", "Marketing", "Stakeholder"],
    "scores": [95, 90, 85, 88, 80]
  },
  "competency_details": [
    {
      "name": "Data-Driven Insight",
      "score": 95,
      "positive_feedback": "분석 프레임워크 활용 능력이 우수함. 시장 수요 예측에 대한 논리가 타당함.",
      "negative_feedback": None,
      "evidence_transcript_id": "TR_015_C01"
    },
    {
      "name": "Strategic Problem Solving",
      "score": 90,
      "positive_feedback": "MECE 원칙에 입각한 문제 분해 능력이 돋보임. 가설 수립 및 검증 과정이 체계적임.",
      "negative_feedback": None,
      "evidence_transcript_id": "TR_015_C02"
    },
    {
      "name": "Value Chain Optimization",
      "score": 85,
      "positive_feedback": "원가 절감 및 생산성 개선에 대한 이해도가 높음.",
      "negative_feedback": "다양한 Value Chain 전반에 대한 깊이 있는 경험은 추가 검증 필요.",
      "evidence_transcript_id": "TR_015_C03"
    },
    {
      "name": "Customer Journey & Marketing Strategy",
      "score": 88,
      "positive_feedback": "타겟 고객 페르소나 정의 및 채널 전략 수립 능력이 우수함.",
      "negative_feedback": None,
      "evidence_transcript_id": "TR_015_C04"
    },
    {
      "name": "Stakeholder Management",
      "score": 80,
      "positive_feedback": "의견 대립 상황에서 데이터 기반 설득 경험이 있음.",
      "negative_feedback": "복잡한 이해관계 조정 경험이 상대적으로 부족함.",
      "evidence_transcript_id": "TR_015_C05"
    }
  ],
  "deep_dive_analysis": [
    {
      "question_topic": "문제 해결 능력",
      "trigger_reason": "초기 답변의 구체성 부족 (Abstract Answer)",
      "initial_question": "가장 어려웠던 문제 해결 경험은 무엇이며, 어떻게 접근했는지 설명해 주십시오.",
      "candidate_initial_response": "매출이 떨어져서 열심히 홍보해서 올렸습니다. 시장 상황이 좋지 않았지만, 저희 팀이 똘똘 뭉쳐 노력한 결과 좋은 성과를 낼 수 있었습니다.",
      "follow_up_question": "단순히 열심히 했다는 답변은 모호합니다. 당시 매출 하락의 근본 원인(Root Cause)은 무엇으로 진단하셨으며, 홍보 후 ROI는 정확히 얼마였습니까?",
      "candidate_response_summary": "당시 20대 유입이 15% 감소한 것이 원인이었고, 인스타그램 광고 집행 후 ROAS(광고수익률) 300%를 달성했습니다. 특정 연령층의 트렌드 변화를 데이터로 포착하여 맞춤형 콘텐츠를 제작한 것이 주효했습니다.",
      "agent_evaluation": "초기 답변은 모호했으나, 압박성 꼬리질문(Deep Dive)에 대해 구체적인 수치(KPI)와 데이터 기반의 판단 근거를 제시하여 역량 입증에 성공함.",
      "score_impact": "+5",
      "transcript_segment_id": "SEG_001"
    },
    {
      "question_topic": "데이터 기반 인사이트",
      "trigger_reason": "트렌드 분석에 대한 피상적인 답변",
      "initial_question": "최근 패션 트렌드 중 가장 인상 깊었던 것은 무엇이며, 이를 삼성물산 패션부문에 어떻게 적용할 수 있을까요?",
      "candidate_initial_response": "친환경 소재와 지속 가능한 패션이 중요한 트렌드라고 생각합니다. 저희도 이런 부분을 강화해야 한다고 봅니다.",
      "follow_up_question": "지속 가능한 패션이 중요하다고 하셨는데, 구체적으로 어떤 데이터를 통해 그 중요성을 파악하셨으며, 삼성물산 패션부문의 어떤 브랜드에, 어떤 방식으로 적용했을 때 가장 큰 비즈니스 효과를 기대할 수 있을까요? 예를 들어, 경쟁사 사례나 소비자 행동 변화 데이터를 들어 설명해 주시겠습니까?",
      "candidate_response_summary": "최근 3년간 국내외 컨슈머 리포트에서 친환경 제품 구매 의향이 20% 이상 증가했으며, 특히 MZ세대에서 가치 소비 경향이 뚜렷합니다. 빈폴(Beanpole)의 경우, 재생 플라스틱을 활용한 원단 사용을 확대하고 제품 생산 이력을 투명하게 공개하는 캠페인을 전개하면, 브랜드 이미지를 제고하고 신규 고객 유입을 5% 이상 늘릴 수 있다고 예상합니다. 이는 경쟁사 파타고니아(Patagonia)의 사례에서 볼 수 있듯이, 기업의 사회적 책임(CSR) 활동이 매출 증대로 이어지는 경향과 일치합니다.",
      "agent_evaluation": "초기 답변은 다소 일반적이었으나, 추가 질문에 대해 구체적인 시장 데이터(컨슈머 리포트, MZ세대 소비 경향)와 경쟁사 사례(파타고니아), 그리고 자사 브랜드(빈폴)에 대한 구체적인 적용 방안 및 예상 효과(신규 고객 유입 5% 증가)를 제시하여 'Data-Driven Insight' 역량을 훌륭하게 보여주었습니다.",
      "score_impact": "+8",
      "transcript_segment_id": "SEG_002"
    }
  ],
  "feedback_loop": {
    "is_reviewed": False,
    "hr_comment": "",
    "adjusted_score": None
  },
  "interview_date": "2024-11-20",
  "priority_review": True,
  "rank": 1
}


router = APIRouter(prefix="/applicants", tags=["applicants"])
logger = logging.getLogger("uvicorn")


@router.get("/{applicant_id}/evaluation-details", response_model=EvaluationDetailResponse)
async def get_applicant_evaluation_details(
    applicant_id: int,
    db: Session = Depends(get_db)
):
    """
    지원자의 상세 평가 리포트 조회

    Args:
        applicant_id: 지원자 ID

    Returns:
        EvaluationDetailResponse: 지원자의 상세 평가 정보
    """
    logger.info(f"Getting evaluation details for applicant ID: {applicant_id}")
    
    # TODO: Replace this with actual service call to fetch and build the response
    # For now, returning mock data. We ignore the applicant_id for now.
    
    # You can add logic here to return different mock data based on applicant_id if needed
    # For example: if applicant_id == 1: return mock_data_1
    
    return candidate_detail_mock



router = APIRouter(prefix="/applicants", tags=["applicants"])
logger = logging.getLogger("uvicorn")


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
    logger.info(f"Creating or updating applicant with email: {email}")
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
    logger.info(f"Getting applicant with ID: {applicant_id}")
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
    logger.info(f"Getting applicants with skip: {skip}, limit: {limit}")
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
    logger.info(f"Updating applicant with ID: {applicant_id}")
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
    logger.info(f"Deleting applicant with ID: {applicant_id}")
    applicant_service = ApplicantService()
    success = applicant_service.delete_applicant(db, applicant_id)

    if not success:
        raise HTTPException(status_code=404, detail="Applicant not found")

    return {"message": f"Applicant {applicant_id} deleted successfully"}
