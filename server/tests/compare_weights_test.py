"""
가중치 비교 테스트 - 데이터 분석 강조 시 김지원 vs 박서진

Usage:
    cd /home/ec2-user/flex/server && python tests/compare_weights_test.py
"""
import sys
import os
import json
import asyncio
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.evaluation.evaluation_service import EvaluationService


async def evaluate_with_weights(name, transcript_path, resume_path, weights, interview_id, applicant_id):
    """특정 가중치로 평가 실행"""

    with open(transcript_path, "r", encoding="utf-8") as f:
        transcript = json.load(f)
    with open(resume_path, "r", encoding="utf-8") as f:
        resume_data = json.load(f)

    service = EvaluationService()

    result = await service.evaluate_interview(
        interview_id=interview_id,
        applicant_id=applicant_id,
        job_id=1,
        transcript=transcript,
        competency_weights=weights,
        resume_data=resume_data
    )

    return {
        "name": name,
        "final_score": result.get("final_score", 0),
        "competency_scores": result.get("competency_scores", {})
    }


async def main():
    data_dir = Path(__file__).resolve().parent.parent / "test_data"

    # 테스트 데이터 경로
    jiwon_transcript = data_dir / "transcript_jiwon_101.json"
    jiwon_resume = data_dir / "resume_jiwon.json"
    seojin_transcript = data_dir / "transcript_박서진_102.json"
    seojin_resume = data_dir / "resume_jiwon.json"  # 같은 이력서 사용

    # 기존 가중치 (균등)
    original_weights = {
        "achievement_motivation": 0.10,
        "growth_potential": 0.10,
        "interpersonal_skill": 0.10,
        "organizational_fit": 0.10,
        "problem_solving": 0.10,
        "customer_journey_marketing": 0.15,
        "md_data_analysis": 0.15,
        "seasonal_strategy_kpi": 0.10,
        "stakeholder_collaboration": 0.05,
        "value_chain_optimization": 0.05,
    }

    # 데이터 분석 강조 가중치
    data_focused_weights = {
        "achievement_motivation": 0.08,
        "growth_potential": 0.08,
        "interpersonal_skill": 0.05,  # 낮춤
        "organizational_fit": 0.08,
        "problem_solving": 0.11,
        "customer_journey_marketing": 0.10,
        "md_data_analysis": 0.25,  # 크게 높임 (0.15 -> 0.25)
        "seasonal_strategy_kpi": 0.10,
        "stakeholder_collaboration": 0.05,
        "value_chain_optimization": 0.10,  # 높임 (0.05 -> 0.10)
    }

    print("\n" + "=" * 80)
    print(" 가중치 비교 테스트 - 데이터 분석 강조")
    print("=" * 80)

    print("\n[기존 가중치]")
    print(f"  md_data_analysis: {original_weights['md_data_analysis']}")
    print(f"  value_chain_optimization: {original_weights['value_chain_optimization']}")
    print(f"  interpersonal_skill: {original_weights['interpersonal_skill']}")
    print(f"  stakeholder_collaboration: {original_weights['stakeholder_collaboration']}")

    print("\n[데이터 분석 강조 가중치]")
    print(f"  md_data_analysis: {data_focused_weights['md_data_analysis']}")
    print(f"  value_chain_optimization: {data_focused_weights['value_chain_optimization']}")
    print(f"  interpersonal_skill: {data_focused_weights['interpersonal_skill']}")
    print(f"  stakeholder_collaboration: {data_focused_weights['stakeholder_collaboration']}")

    print("\n" + "-" * 80)
    print(" 평가 실행 중... (시간이 걸릴 수 있습니다)")
    print("-" * 80)

    # 김지원 - 데이터 분석 강조 가중치
    print("\n1. 김지원 평가 (데이터 분석 강조)...")
    jiwon_result = await evaluate_with_weights(
        "김지원", jiwon_transcript, jiwon_resume,
        data_focused_weights, 101, 101
    )

    # 박서진 - 데이터 분석 강조 가중치
    print("2. 박서진 평가 (데이터 분석 강조)...")
    seojin_result = await evaluate_with_weights(
        "박서진", seojin_transcript, seojin_resume,
        data_focused_weights, 102, 102
    )

    print("\n" + "=" * 80)
    print(" 결과 비교 (데이터 분석 강조 가중치 적용)")
    print("=" * 80)

    print(f"\n  김지원: {jiwon_result['final_score']:.1f}점")
    print(f"  박서진: {seojin_result['final_score']:.1f}점")
    print(f"  차이: {jiwon_result['final_score'] - seojin_result['final_score']:.1f}점")

    print("\n[역량별 점수 비교]")
    print(f"{'역량':<30} {'김지원':>10} {'박서진':>10} {'차이':>10}")
    print("-" * 60)

    for comp in data_focused_weights.keys():
        jiwon_score = jiwon_result['competency_scores'].get(comp, {}).get('overall_score', 0)
        seojin_score = seojin_result['competency_scores'].get(comp, {}).get('overall_score', 0)
        diff = jiwon_score - seojin_score
        weight = data_focused_weights[comp]
        print(f"{comp:<30} {jiwon_score:>10.0f} {seojin_score:>10.0f} {diff:>+10.0f}  (w={weight})")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
