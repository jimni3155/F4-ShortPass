"""
김지원 - 데이터 분석 강조 가중치 테스트
"""
import sys
import os
import json
import asyncio
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.evaluation.evaluation_service import EvaluationService


async def main():
    data_dir = Path(__file__).resolve().parent.parent / "test_data"

    with open(data_dir / "transcript_jiwon_101.json", "r", encoding="utf-8") as f:
        transcript = json.load(f)
    with open(data_dir / "resume_jiwon.json", "r", encoding="utf-8") as f:
        resume_data = json.load(f)

    # 데이터 분석 강조 가중치
    weights = {
        "achievement_motivation": 0.08,
        "growth_potential": 0.08,
        "interpersonal_skill": 0.05,
        "organizational_fit": 0.08,
        "problem_solving": 0.11,
        "customer_journey_marketing": 0.10,
        "md_data_analysis": 0.25,  # 높임
        "seasonal_strategy_kpi": 0.10,
        "stakeholder_collaboration": 0.05,
        "value_chain_optimization": 0.10,  # 높임
    }

    print(f"가중치 합계: {sum(weights.values())}")
    print("김지원 평가 시작...")

    service = EvaluationService()
    result = await service.evaluate_interview(
        interview_id=101,
        applicant_id=101,
        job_id=1,
        transcript=transcript,
        competency_weights=weights,
        resume_data=resume_data
    )

    print(f"\n김지원 최종 점수: {result.get('final_score', 0):.1f}점")


if __name__ == "__main__":
    asyncio.run(main())
