# server/ai/agents/graph/nodes.py
"""
LangGraph Nodes
각 단계별 Node 함수 정의
"""

from typing import Dict
from graph.state import EvaluationState
from agents.competency_agent import CompetencyAgent, evaluate_all_competencies
from aggregators.job_aggregator import JobAggregator
from aggregators.common_aggregator import CommonAggregator
from validators.confidence_validator import ConfidenceValidator


# ============================================
# 1. 배치 평가 Node (10개 Agent 동시 실행)
# ============================================

async def batch_evaluation_node(state: EvaluationState) -> EvaluationState:
    """
    10개 역량 배치 평가 Node
    
    이 Node에서 10개 Agent를 asyncio.gather로 병렬 실행
    """
    print("\n" + "="*60)
    print("[Node] 배치 평가 시작 (10개 역량 병렬 실행)")
    print("="*60)
    
    # 1. Agent 생성
    agent = CompetencyAgent(
        state["openai_client"],
        max_concurrent=5  # 최대 5개씩 동시 실행
    )
    
    # 2. 10개 역량 배치 평가
    all_results = await evaluate_all_competencies(
        agent,
        state["transcript"],
        state["prompts"]
    )
    
    # 3. State 업데이트
    state["problem_solving_result"] = all_results["problem_solving"]
    state["organizational_fit_result"] = all_results["organizational_fit"]
    state["growth_potential_result"] = all_results["growth_potential"]
    state["interpersonal_skills_result"] = all_results["interpersonal_skills"]
    state["achievement_motivation_result"] = all_results["achievement_motivation"]
    state["structured_thinking_result"] = all_results["structured_thinking"]
    state["business_documentation_result"] = all_results["business_documentation"]
    state["financial_literacy_result"] = all_results["financial_literacy"]
    state["industry_learning_result"] = all_results["industry_learning"]
    state["stakeholder_management_result"] = all_results["stakeholder_management"]
    
    print("\n[Node] 배치 평가 완료")
    
    return state


# ============================================
# 2. Job Aggregator Node
# ============================================

async def job_aggregator_node(state: EvaluationState) -> EvaluationState:
    """Job 5개 역량 통합 Node"""
    
    print("\n" + "="*60)
    print("[Node] Job 통합 시작")
    print("="*60)
    
    # Job 5개 결과 추출
    job_results = {
        "structured_thinking": state["structured_thinking_result"],
        "business_documentation": state["business_documentation_result"],
        "financial_literacy": state["financial_literacy_result"],
        "industry_learning": state["industry_learning_result"],
        "stakeholder_management": state["stakeholder_management_result"],
    }
    
    # 통합
    job_aggregation = JobAggregator.aggregate(job_results, state["job_weights"])
    
    # State 업데이트
    state["job_aggregation_result"] = job_aggregation
    
    print(f"[Node] Job 통합 완료: {job_aggregation['overall_job_score']}점")
    
    return state


# ============================================
# 3. Common Aggregator Node
# ============================================

async def common_aggregator_node(state: EvaluationState) -> EvaluationState:
    """Common 5개 역량 통합 Node"""
    
    print("\n" + "="*60)
    print("[Node] Common 통합 시작")
    print("="*60)
    
    # Common 5개 결과 추출
    common_results = {
        "problem_solving": state["problem_solving_result"],
        "organizational_fit": state["organizational_fit_result"],
        "growth_potential": state["growth_potential_result"],
        "interpersonal_skills": state["interpersonal_skills_result"],
        "achievement_motivation": state["achievement_motivation_result"],
    }
    
    # 통합
    common_aggregation = CommonAggregator.aggregate(common_results, state["common_weights"])
    
    # State 업데이트
    state["common_aggregation_result"] = common_aggregation
    
    print(f"[Node] Common 통합 완료: {common_aggregation['overall_common_score']}점")
    
    return state


# ============================================
# 4. Confidence Validator Node
# ============================================

async def confidence_validator_node(state: EvaluationState) -> EvaluationState:
    """신뢰도 검증 Node"""
    
    print("\n" + "="*60)
    print("[Node] 신뢰도 검증 시작")
    print("="*60)
    
    # 검증
    validation = ConfidenceValidator.validate(
        state["job_aggregation_result"],
        state["common_aggregation_result"],
        threshold=0.7
    )
    
    # State 업데이트
    state["low_confidence_competencies"] = validation["low_confidence_competencies"]
    state["validation_notes"] = validation["validation_notes"]
    state["requires_revaluation"] = validation["requires_revaluation"]
    
    print(f"[Node] 검증 완료: {validation['validation_notes']}")
    
    return state