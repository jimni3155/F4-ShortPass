"""
김지원 면접 평가 테스트 스크립트
transcript_jiwon_101.json으로 evaluation 실행
"""
import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path, override=True)

from openai import AsyncOpenAI
from ai.agents.graph.evaluation import create_evaluation_graph

# 프롬프트 생성 함수 import
# Common Competencies
from ai.prompts.competency_agents.common_competencies.problem_solving_prompt import create_problem_solving_evaluation_prompt
from ai.prompts.competency_agents.common_competencies.organizational_fit_prompt import create_organizational_fit_evaluation_prompt
from ai.prompts.competency_agents.common_competencies.growth_potential_prompt import create_growth_potential_evaluation_prompt
from ai.prompts.competency_agents.common_competencies.interpersonal_skill_prompt import create_interpersonal_skill_evaluation_prompt
from ai.prompts.competency_agents.common_competencies.achievement_motivation_prompt import create_achievement_motivation_evaluation_prompt

# Job Competencies
from ai.prompts.competency_agents.job_competencies.customer_journey_marketing_prompt import create_customer_journey_marketing_evaluation_prompt
from ai.prompts.competency_agents.job_competencies.data_analysis_prompt import create_md_data_analysis_evaluation_prompt
from ai.prompts.competency_agents.job_competencies.seasonal_strategy_kpi_prompt import create_seasonal_strategy_kpi_evaluation_prompt
from ai.prompts.competency_agents.job_competencies.stakeholder_collaboration_prompt import create_stakeholder_collaboration_evaluation_prompt
from ai.prompts.competency_agents.job_competencies.value_chain_optimization_prompt import create_value_chain_optimization_evaluation_prompt


PROMPT_GENERATORS = {
    # Common (5개)
    "problem_solving": create_problem_solving_evaluation_prompt,
    "organizational_fit": create_organizational_fit_evaluation_prompt,
    "growth_potential": create_growth_potential_evaluation_prompt,
    "interpersonal_skill": create_interpersonal_skill_evaluation_prompt,
    "achievement_motivation": create_achievement_motivation_evaluation_prompt,
    # Job (5개)
    "customer_journey_marketing": create_customer_journey_marketing_evaluation_prompt,
    "md_data_analysis": create_md_data_analysis_evaluation_prompt,
    "seasonal_strategy_kpi": create_seasonal_strategy_kpi_evaluation_prompt,
    "stakeholder_collaboration": create_stakeholder_collaboration_evaluation_prompt,
    "value_chain_optimization": create_value_chain_optimization_evaluation_prompt,
}


async def test_jiwon_evaluation():
    """김지원 면접 평가 테스트"""

    # 데이터 로드
    data_dir = Path(__file__).parent.parent / "test_data"
    transcript_path = data_dir / "transcript_jiwon_101.json"

    with open(transcript_path, "r", encoding="utf-8") as f:
        transcript = json.load(f)

    print("\n" + "="*80)
    print("  김지원 면접 평가 테스트")
    print("="*80)
    print(f"  Transcript: {len(transcript['segments'])}개 segment")
    print(f"  기대 프로필: 데이터는 잘하는데 사람이 힘든 타입")
    print("="*80)

    # OpenAI 클라이언트
    openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # 프롬프트 생성
    transcript_str = json.dumps(transcript, ensure_ascii=False, indent=2)
    prompts = {
        name: generator(transcript_str)
        for name, generator in PROMPT_GENERATORS.items()
    }

    # 가중치 설정 (공통역량만 테스트)
    common_weights = {
        "problem_solving": 0.20,
        "organizational_fit": 0.20,
        "growth_potential": 0.20,
        "interpersonal_skills": 0.20,
        "achievement_motivation": 0.20
    }

    # 그래프 생성 및 실행
    graph = create_evaluation_graph()

    initial_state = {
        "interview_id": 101,
        "applicant_id": 101,
        "job_id": 1,
        "transcript": transcript,
        "transcript_content": transcript_str,  # nodes.py에서 필요
        "openai_client": openai_client,
        "prompts": prompts,
        "job_weights": {},  # 직무역량은 빈 dict
        "common_weights": common_weights,
        "job_common_ratio": {"job": 0.0, "common": 1.0},  # 공통역량만

        # 초기화
        "structured_thinking_result": None,
        "business_documentation_result": None,
        "financial_literacy_result": None,
        "industry_learning_result": None,
        "stakeholder_management_result": None,
        "problem_solving_result": None,
        "organizational_fit_result": None,
        "growth_potential_result": None,
        "interpersonal_skills_result": None,
        "achievement_motivation_result": None,
        "job_aggregation_result": None,
        "common_aggregation_result": None,
        "low_confidence_competencies": [],
        "validation_notes": None,
        "requires_revaluation": False,
        "evidence_conflicts": [],
        "low_confidence_list": [],
        "requires_collaboration": False,
        "mediation_results": [],
        "adversarial_results": [],
        "collaboration_count": 0,
        "final_score": None,
        "avg_confidence": None,
        "final_reliability": None,
        "reliability_note": None,
        "final_result": None,
        "started_at": datetime.now(),
        "completed_at": None,
        "errors": [],
        "execution_logs": [],
        "structured_transcript": None
    }

    print("\n평가 시작...")
    result = await graph.ainvoke(initial_state)

    # 결과 출력
    print("\n" + "="*80)
    print("  평가 결과")
    print("="*80)

    # 공통역량 결과 추출
    final_result = result.get("final_result", {})
    common_agg = result.get("common_aggregation_result", {})

    print("\n[공통역량 점수]")
    print("-"*60)

    competency_names = {
        "problem_solving": "문제해결력",
        "interpersonal_skills": "대인관계능력",
        "achievement_motivation": "성취동기",
        "growth_potential": "성장잠재력",
        "organizational_fit": "조직적합성"
    }

    for comp_key, comp_name in competency_names.items():
        comp_result = result.get(f"{comp_key}_result", {})
        if comp_result:
            score = comp_result.get("overall_score", "N/A")
            confidence = comp_result.get("confidence", {}).get("overall", "N/A")
            print(f"  {comp_name}: {score}점 (신뢰도: {confidence})")

            # Red Flags 출력
            red_flags = comp_result.get("red_flags", [])
            if red_flags:
                print(f"    ⚠️ Red Flags: {red_flags}")

    print("\n" + "-"*60)
    print(f"최종 점수: {result.get('final_score', 'N/A')}점")
    print(f"평균 신뢰도: {result.get('avg_confidence', 'N/A')}")
    print(f"최종 신뢰등급: {result.get('final_reliability', 'N/A')}")

    # 결과 저장
    output_path = data_dir / "evaluation_result_jiwon_test.json"

    # 직렬화 가능한 형태로 변환
    serializable_result = {
        "interview_id": 101,
        "applicant_id": 101,
        "final_score": result.get("final_score"),
        "avg_confidence": result.get("avg_confidence"),
        "final_reliability": result.get("final_reliability"),
        "competency_results": {}
    }

    for comp_key in competency_names.keys():
        comp_result = result.get(f"{comp_key}_result", {})
        if comp_result:
            serializable_result["competency_results"][comp_key] = comp_result

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(serializable_result, f, ensure_ascii=False, indent=2, default=str)

    print(f"\n결과 저장: {output_path}")

    return result


if __name__ == "__main__":
    asyncio.run(test_jiwon_evaluation())
