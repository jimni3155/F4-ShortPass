# api/endpoints/evaluation.py
"""
평가 관련 API 엔드포인트
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from services.evaluation.evaluation_service import EvaluationService
from services.evaluation.evaluation_query_service import EvaluationQueryService
from services.evaluation.evaluation_stats_service import EvaluationStatsService
from ai.utils.llm_client import LLMClient
from db.database import get_db


# Pydantic Models for Evaluation Results
class LinkedUtterance(BaseModel):
    id: int
    speaker: str
    text: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None

class EvidenceItem(BaseModel):
    turn: int
    quote: str
    observation: str
    dimension: str
    impact: str
    jd_match: Optional[str] = None
    linked_utterance: Optional[LinkedUtterance] = None

class TriggeredFlag(BaseModel):
    flag: str
    turn: int
    quote: str
    impact: str

class TriggeredFlags(BaseModel):
    green: List[TriggeredFlag] = []
    red: List[TriggeredFlag] = []

class DynamicCriterionScore(BaseModel):
    name: str
    score: int
    standard_comparison: str
    justification: str

class TechnicalSkillMatch(BaseModel):
    skill: str
    experience_years: Optional[int] = None
    depth: Optional[str] = None

class MissingSkill(BaseModel):
    skill: str
    reason: str

class TechnicalSkillsCoverage(BaseModel):
    required_skills_matched: int
    required_skills_total: int
    coverage_percentage: int
    matched_skills: List[TechnicalSkillMatch] = []
    missing_skills: List[MissingSkill] = []
    preferred_skills_matched: List[str] = []
    preferred_skills_bonus: int = 0

class SubScore(BaseModel):
    score: int
    standard_comparison: str
    justification: str

class KeyObservationPattern(BaseModel):
    positive_patterns: List[str] = []
    negative_patterns: List[str] = []
    portfolio_interview_consistency: Optional[str] = None
    production_experience_level: Optional[str] = None

class CompetencyReasoningLog(BaseModel):
    score: int
    matched_standard: str
    reasoning: str
    evidence: List[EvidenceItem]
    triggered_flags: TriggeredFlags
    dynamic_criteria_scores: Dict[str, DynamicCriterionScore]
    technical_skills_coverage: Optional[TechnicalSkillsCoverage] = None
    sub_scores: Dict[str, SubScore]
    strengths: List[str]
    areas_for_improvement: List[str]
    key_observations: KeyObservationPattern
    interviewer_notes: str

class EvaluationResultResponse(BaseModel):
    evaluation_id: int
    applicant_id: int
    job_id: int
    match_score: float
    normalized_score: Optional[float] = None
    overall_feedback: Optional[str] = None
    hiring_recommendation: Optional[str] = None
    reasoning_log: Dict[str, CompetencyReasoningLog] # This will hold the detailed competency logs

router = APIRouter(prefix="/evaluations", tags=["Evaluations"])

# 서비스 초기화
llm_client = LLMClient()
evaluation_service = EvaluationService(llm_client)
query_service = EvaluationQueryService()
stats_service = EvaluationStatsService()


# ==================== 1. 평가 실행 ====================

@router.post("/execute")
async def execute_evaluation(
    interview_id: int = Query(..., description="면접 세션 ID"),
    job_id: int = Query(..., description="채용 공고 ID"),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    면접 완료 후 평가 실행 (1:1 매칭)
    
    Flow:
    1. DB에 평가 레코드 생성 (상태: pending)
    2. 백그라운드로 LangGraph 실행
    3. 즉시 evaluation_id 반환
    
    Returns:
        - success: bool
        - evaluation_id: int
        - status: 'processing'
    """
    try:
        # 평가 레코드 생성
        evaluation_id = await evaluation_service.create_pending_evaluation(
            db=db,
            interview_id=interview_id,
            job_id=job_id
        )
        
        # 백그라운드로 실제 평가 실행
        background_tasks.add_task(
            evaluation_service.run_evaluation_for_application,
            interview_id=interview_id,
            job_id=job_id,
            evaluation_id=evaluation_id
        )
        
        return {
            "success": True,
            "evaluation_id": evaluation_id,
            "status": "processing",
            "message": "Evaluation started in background"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 2. 구직자용 - 평가 결과 조회 ====================

@router.get("/applicants/{applicant_id}/result/{evaluation_id}", response_model=EvaluationResultResponse)
async def get_evaluation_result_for_applicant(
    applicant_id: int,
    evaluation_id: int,
    db: Session = Depends(get_db)
):
    """
    구직자용 - 평가 결과 조회 (성장 중심 + 근거 필수)
    
    Returns:
        - status: 평가 상태
        - competencies: 6개 역량별 평가 (점수 + 근거 + 개선 방법)
        - overall_feedback: 종합 피드백
        - top_strengths: 전체 강점 Top 5
        - key_improvements: 핵심 개선사항 Top 3
    """
    try:
        result = await query_service.get_evaluation_for_applicant(
            db=db,
            applicant_id=applicant_id,
            evaluation_id=evaluation_id
        )
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ==================== 3. 기업용 - 지원자 평가 조회 ====================

@router.get("/jobs/{job_id}/applicants/{applicant_id}/result", response_model=EvaluationResultResponse)
async def get_applicant_evaluation_for_company(
    job_id: int,
    applicant_id: int,
    db: Session = Depends(get_db)
):
    """
    기업용 - 지원자 평가 상세 (채용 판단 중심 + 근거 필수)

    Returns:
        - status: 평가 상태
        - competencies: 6개 역량별 상세 평가 (evidence, flags, detailed_rationale 포함)
        - hiring_recommendation: 채용 추천
        - job_requirement_fit_score: JD 요구사항 충족도
        - key_insights: 핵심 인사이트 (근거 포함)
        - overall_feedback: 종합 피드백
    """
    try:
        result = await query_service.get_evaluation_for_company(
            db=db,
            job_id=job_id,
            applicant_id=applicant_id
        )
        return result

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/jobs/{job_id}/applicants/{applicant_id}/evidence")
async def get_evaluation_evidence(
    job_id: int,
    applicant_id: int,
    competency: Optional[str] = Query(None, description="특정 역량 필터 (예: data_driven)"),
    db: Session = Depends(get_db)
):
    """
    평가 근거 상세 조회 - Transcript 기반 증거 제시

    멘토 요구사항 반영:
    "알고리즘 산출 과정이 아니라, 실제 면접 내용을 보여줘야 신뢰를 얻는다"
    "어떤 질문에 어떤 응답을 했는지 그 자체를 근거로"

    사용 시나리오:
    1. 결과 페이지에서 역량 차트 클릭 시
    2. 해당 역량의 평가 근거 (질문, 답변, 하이라이트) 표시

    Returns:
        {
            "applicant_name": "박서연",
            "overall_score": 75.5,
            "competency_evidences": [
                {
                    "competency": "data_driven",
                    "competency_name": "데이터 기반 의사결정",
                    "score": 85,
                    "evidence_sentences": [
                        "6개월치 광고 데이터를 수집해서 엑셀로 피벗 테이블을 만들고...",
                        "채널별 전환율과 ROI를 계산했습니다"
                    ],
                    "positive_keywords": ["데이터", "엑셀", "피벗 테이블", "전환율", "ROI"],
                    "negative_keywords": [],
                    "justification": "데이터 기반 의사결정 역량에서 우수한 평가...",
                    "relevant_qa": [
                        {
                            "question": "데이터를 활용해 비즈니스 문제를 해결했던 경험은?",
                            "answer": "이전 인턴십에서 마케팅 캠페인..."
                        }
                    ]
                }
            ],
            "strengths": [...],
            "weaknesses": [...]
        }
    """
    from services.evaluation.evidence_extractor import EvidenceExtractor
    from models.interview import InterviewSession, InterviewResult, Applicant

    try:
        # 1. Interview Session 조회
        interview = db.query(InterviewSession).join(
            Applicant, InterviewSession.applicant_id == Applicant.id
        ).filter(
            InterviewSession.applicant_id == applicant_id
        ).first()

        if not interview:
            raise HTTPException(
                status_code=404,
                detail=f"Interview not found for applicant {applicant_id}"
            )

        # 2. Applicant 정보
        applicant = db.query(Applicant).filter(Applicant.id == applicant_id).first()

        # 3. Interview Results (질문-답변 쌍)
        results = db.query(InterviewResult).filter(
            InterviewResult.interview_id == interview.id
        ).all()

        if not results:
            raise HTTPException(
                status_code=404,
                detail=f"No interview results found for interview {interview.id}"
            )

        # 4. QA 쌍 구성
        qa_pairs = []
        all_scores = {}

        for result in results:
            qa_pairs.append({
                "question": result.question_text,
                "answer": result.stt_full_text,
                "target_competencies": list(result.scores.keys()) if result.scores else []
            })

            # 점수 수집
            if result.scores:
                for comp, score in result.scores.items():
                    if comp not in all_scores:
                        all_scores[comp] = []
                    all_scores[comp].append(score)

        # 5. 평균 점수 계산
        competency_scores = {
            comp: sum(scores) / len(scores)
            for comp, scores in all_scores.items()
        }

        # 6. Evidence Extractor 사용
        extractor = EvidenceExtractor()

        # 특정 역량만 필터링
        if competency:
            if competency not in competency_scores:
                raise HTTPException(
                    status_code=404,
                    detail=f"Competency '{competency}' not found in evaluation"
                )
            competency_scores = {competency: competency_scores[competency]}

        # 7. 증거 추출
        evidences = extractor.extract_all_evidences(
            qa_pairs=qa_pairs,
            competency_scores=competency_scores
        )

        # 8. 강점/약점 추출
        strengths_weaknesses = extractor.extract_strengths_weaknesses(
            competency_scores=competency_scores,
            evidences=evidences,
            top_n=3
        )

        # 9. 전체 점수 계산
        overall_score = sum(competency_scores.values()) / len(competency_scores) if competency_scores else 0

        return {
            "applicant_name": applicant.name if applicant else "Unknown",
            "overall_score": round(overall_score, 1),
            "competency_evidences": evidences,
            "strengths": strengths_weaknesses["strengths"],
            "weaknesses": strengths_weaknesses["weaknesses"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting evidence: {str(e)}")


@router.get("/jobs/{job_id}/applicants")
async def get_all_applicants_for_job(
    job_id: int,
    # 필터링 옵션
    min_score: float = Query(0, ge=0, le=100, description="최소 종합 점수"),
    max_score: float = Query(100, ge=0, le=100, description="최대 종합 점수"),
    min_experience_years: Optional[int] = Query(None, description="최소 경력 연수"),
    education_filter: Optional[str] = Query(None, description="학력 필터 (예: 대졸, 석사)"),
    keyword_include: Optional[str] = Query(None, description="포함할 키워드 (쉼표 구분)"),
    keyword_exclude: Optional[str] = Query(None, description="제외할 키워드 (쉼표 구분)"),
    competency_focus: Optional[str] = Query(None, description="중점 역량 필터 (예: data_driven)"),
    min_competency_score: Optional[float] = Query(None, description="중점 역량 최소 점수"),
    # 정렬 옵션
    sort_by: str = Query(
        "overall_score",
        description="정렬 기준: overall_score | common_competency | job_competency | specific_competency"
    ),
    sort_order: str = Query("desc", description="정렬 순서: asc | desc"),
    # 페이지네이션
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    db: Session = Depends(get_db)
):
    """
    기업용 - 모든 지원자 목록 (고급 필터링 및 정렬)

    멘토 요구사항 반영:
    - "점수만으로 판단하지 말고, Transcript를 source of truth로 활용"
    - "HR이 다양한 조건으로 지원자를 효율적으로 분류/선별"

    필터링 옵션:
    - 점수 범위 (min_score, max_score)
    - 경력 연수 (min_experience_years)
    - 학력 (education_filter)
    - 키워드 포함/제외 (keyword_include, keyword_exclude)
    - 특정 역량 중심 (competency_focus, min_competency_score)

    정렬 옵션:
    - overall_score: 종합 점수순
    - common_competency: 공통 역량 평균순
    - job_competency: 직무 역량 평균순
    - specific_competency: 특정 역량순 (competency_focus 필요)

    Returns:
        {
            "total_count": 50,
            "filtered_count": 15,
            "page": 1,
            "page_size": 20,
            "applicants": [
                {
                    "applicant_id": 1,
                    "name": "박서연",
                    "overall_score": 75.5,
                    "common_competency_avg": 72.0,
                    "job_competency_avg": 79.0,
                    "top_strengths": ["데이터 분석", "전략적 사고"],
                    "top_weaknesses": ["산업 이해도"],
                    "recommendation": "추천",
                    "education": "서울대 경영학과",
                    "experience_years": 3
                }
            ]
        }
    """
    from models.interview import InterviewSession, InterviewResult, Applicant
    from sqlalchemy import and_, or_

    try:
        # 1. 기본 쿼리 구성
        query = db.query(
            Applicant.id,
            Applicant.name,
            Applicant.education,
            Applicant.total_experience_years,
            InterviewSession.id.label("interview_id")
        ).join(
            InterviewSession,
            InterviewSession.applicant_id == Applicant.id
        ).filter(
            InterviewSession.company_id == job_id  # job_id가 실제로는 company_id일 수 있음
        )

        # 2. 필터 적용
        if min_experience_years is not None:
            query = query.filter(Applicant.total_experience_years >= min_experience_years)

        if education_filter:
            query = query.filter(Applicant.education.ilike(f"%{education_filter}%"))

        # 3. 지원자 목록 조회
        applicants_raw = query.all()
        total_count = len(applicants_raw)

        # 4. 각 지원자별 평가 점수 및 키워드 계산
        applicants_data = []

        for app in applicants_raw:
            # Interview Results 조회
            results = db.query(InterviewResult).filter(
                InterviewResult.interview_id == app.interview_id
            ).all()

            if not results:
                continue

            # 점수 집계
            all_scores = {}
            all_keywords = set()

            for result in results:
                if result.scores:
                    for comp, score in result.scores.items():
                        if comp not in all_scores:
                            all_scores[comp] = []
                        all_scores[comp].append(score)

                # 키워드 추출
                if result.keywords:
                    if "matched" in result.keywords:
                        all_keywords.update(result.keywords["matched"])

            # 평균 점수 계산
            competency_scores = {
                comp: sum(scores) / len(scores)
                for comp, scores in all_scores.items()
            }

            overall_score = sum(competency_scores.values()) / len(competency_scores) if competency_scores else 0

            # 공통 역량 vs 직무 역량 구분 (예시)
            common_comps = ["communication", "problem_solving", "learning_attitude"]
            job_comps = ["strategic_thinking", "data_driven", "industry_knowledge"]

            common_avg = sum([competency_scores.get(c, 0) for c in common_comps]) / len(common_comps) if common_comps else 0
            job_avg = sum([competency_scores.get(c, 0) for c in job_comps]) / len(job_comps) if job_comps else 0

            # 점수 필터
            if overall_score < min_score or overall_score > max_score:
                continue

            # 역량 필터
            if competency_focus and min_competency_score:
                if competency_scores.get(competency_focus, 0) < min_competency_score:
                    continue

            # 키워드 필터
            if keyword_include:
                include_keywords = [k.strip() for k in keyword_include.split(",")]
                if not any(k in all_keywords for k in include_keywords):
                    continue

            if keyword_exclude:
                exclude_keywords = [k.strip() for k in keyword_exclude.split(",")]
                if any(k in all_keywords for k in exclude_keywords):
                    continue

            # 강점/약점 추출
            sorted_comps = sorted(competency_scores.items(), key=lambda x: x[1], reverse=True)
            top_strengths = [comp for comp, score in sorted_comps[:2] if score >= 70]
            top_weaknesses = [comp for comp, score in sorted_comps[-2:] if score < 60]

            # 추천 여부
            recommendation = "적극 추천" if overall_score >= 80 else "추천" if overall_score >= 70 else "검토 필요"

            applicants_data.append({
                "applicant_id": app.id,
                "name": app.name,
                "overall_score": round(overall_score, 1),
                "common_competency_avg": round(common_avg, 1),
                "job_competency_avg": round(job_avg, 1),
                "competency_scores": competency_scores,
                "top_strengths": top_strengths,
                "top_weaknesses": top_weaknesses,
                "recommendation": recommendation,
                "education": app.education,
                "experience_years": app.total_experience_years,
                "keywords": list(all_keywords)[:10]  # Top 10 keywords
            })

        # 5. 정렬
        reverse = (sort_order == "desc")

        if sort_by == "overall_score":
            applicants_data.sort(key=lambda x: x["overall_score"], reverse=reverse)
        elif sort_by == "common_competency":
            applicants_data.sort(key=lambda x: x["common_competency_avg"], reverse=reverse)
        elif sort_by == "job_competency":
            applicants_data.sort(key=lambda x: x["job_competency_avg"], reverse=reverse)
        elif sort_by == "specific_competency" and competency_focus:
            applicants_data.sort(
                key=lambda x: x["competency_scores"].get(competency_focus, 0),
                reverse=reverse
            )

        # 6. 페이지네이션
        filtered_count = len(applicants_data)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_data = applicants_data[start_idx:end_idx]

        return {
            "total_count": total_count,
            "filtered_count": filtered_count,
            "page": page,
            "page_size": page_size,
            "total_pages": (filtered_count + page_size - 1) // page_size,
            "applicants": paginated_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching applicants: {str(e)}")


# ==================== 4. 통계 & 모니터링 ====================

@router.get("/jobs/{job_id}/statistics")
async def get_job_evaluation_statistics(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    채용 공고별 평가 통계 (편향 모니터링용)
    
    Returns:
        - total_evaluations: 전체 평가 수
        - average_score: 평균 점수
        - median_score: 중간값
        - std_deviation: 표준편차
        - score_distribution: 점수 분포
        - competency_averages: 역량별 평균
        - bias_warnings: 편향 경고
    """
    try:
        result = await stats_service.get_evaluation_statistics(
            db=db,
            job_id=job_id
        )
        return result
        
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
        - total_evaluations: 전체 평가 수
        - job_statistics: 직무별 통계
        - overall_average_score: 전체 평균 점수
        - normalization_metrics: 정규화 필요 여부
        - bias_warnings: 편향 경고
    """
    try:
        result = await stats_service.get_company_statistics(
            db=db,
            company_id=company_id
        )
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ==================== 5. 관리자 / 디버깅 ====================

@router.post("/{evaluation_id}/normalize")
async def normalize_evaluation_scores(
    evaluation_id: int,
    db: Session = Depends(get_db)
):
    """
    평가 점수 정규화 (편향 방지)
    
    같은 job_id의 다른 평가들과 비교하여 Z-score 정규화
    
    Returns:
        - success: bool
        - original_score: float
        - normalized_score: float
        - normalization_method: str
        - statistics: dict
    """
    try:
        result = await stats_service.normalize_scores(
            db=db,
            evaluation_id=evaluation_id
        )
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{evaluation_id}/reasoning-log")
async def get_reasoning_log(
    evaluation_id: int,
    db: Session = Depends(get_db)
):
    """
    AI 추론 로그 조회 (디버깅/검증용)
    
    Returns:
        - evaluation_id: int
        - execution_logs: 각 agent별 실행 시간 및 에러
        - total_execution_time_ms: int
        - evaluator_outputs: 각 evaluator의 원본 JSON
        - aggregator_reasoning: aggregator 추론 과정
    """
    try:
        result = await stats_service.get_reasoning_log(
            db=db,
            evaluation_id=evaluation_id
        )
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
