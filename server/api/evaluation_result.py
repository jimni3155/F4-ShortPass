import json
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

router = APIRouter(prefix="/evaluation-result")


# 로컬 파일 경로
TRANSCRIPT_LOCAL_PATH = os.path.abspath(
    "server/test_data/transcript_jiwon_101.json"
)
EVALUATION_RESULT_PATH = os.path.abspath(
    "server/test_data/a.json"
)


class EvaluationResultResponse(BaseModel):
    """평가 결과 + transcript 통합 응답 모델"""
    applicant: Dict[str, Any]
    transcript: List[Dict[str, Any]]
    overall_summary: Dict[str, Any]
    score_breakdown: Dict[str, Any]
    competency_scores: List[Dict[str, Any]]
    competency_details: Dict[str, Any]


@router.get(
    "/{applicant_id}",
    response_model=EvaluationResultResponse,
    summary="평가 결과 조회",
    description="지원자의 면접 transcript와 평가 결과를 통합하여 반환합니다."
)
async def get_evaluation_result(applicant_id: str):
    """
    평가 결과 조회 엔드포인트
    
    Args:
        applicant_id: 지원자 ID
    
    Returns:
        EvaluationResultResponse: 지원자 정보, transcript, 평가 결과 통합 데이터
    """
    try:
        # 1. Transcript 로드
        if not os.path.exists(TRANSCRIPT_LOCAL_PATH):
            raise HTTPException(
                status_code=404,
                detail=f"Transcript file not found: {TRANSCRIPT_LOCAL_PATH}"
            )
        
        with open(TRANSCRIPT_LOCAL_PATH, 'r', encoding='utf-8') as f:
            transcript_data = json.load(f)
        
        # 2. 평가 결과 로드
        if not os.path.exists(EVALUATION_RESULT_PATH):
            raise HTTPException(
                status_code=404,
                detail=f"Evaluation result file not found: {EVALUATION_RESULT_PATH}"
            )
        
        with open(EVALUATION_RESULT_PATH, 'r', encoding='utf-8') as f:
            evaluation_data = json.load(f)
        
        
        # 3. 통합 응답 생성
        response_data = {
            "applicant": applicant_info,
            "transcript": transcript_data.get("segments", []),
            **evaluation_data
        }
        
        return JSONResponse(content=response_data)
    
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse JSON file: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )