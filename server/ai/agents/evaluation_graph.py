# ai/agents/evaluation_graph.py
"""
LangGraph 기반 평가 시스템
6개 evaluator를 병렬 실행하고 결과를 통합
"""

import operator
from typing import Annotated
from langgraph.graph import StateGraph, END
from datetime import datetime

from ai.agents.state import EvaluationState
from ai.agents.evaluator_nodes import EvaluatorNodes
from ai.agents.aggregator_node import AggregatorNode
from ai.utils.llm_client import LLMClient


def create_evaluation_graph(llm_client: LLMClient):
    """
    평가 그래프 생성
    
    Flow:
    1. START
    2. [병렬] 6개 evaluator 동시 실행
    3. [순차] Aggregator - 결과 통합
    4. [향후] Adversarial Validator (주석으로 위치 표시)
    5. [향후] Refiner (주석으로 위치 표시)
    6. END
    
    Args:
        llm_client: LLM 클라이언트
    
    Returns:
        컴파일된 LangGraph
    """
    # 노드 인스턴스 생성
    evaluators = EvaluatorNodes(llm_client)
    aggregator = AggregatorNode(llm_client)
    
    # State Graph 정의 (execution_logs는 리스트 병합)
    graph = StateGraph(EvaluationState)
    
    # ==================== 6개 Evaluator 노드 등록 ====================
    graph.add_node("job_expertise", evaluators.job_expertise_evaluator)
    graph.add_node("analytical", evaluators.analytical_evaluator)
    graph.add_node("execution", evaluators.execution_evaluator)
    graph.add_node("relationship", evaluators.relationship_evaluator)
    graph.add_node("resilience", evaluators.resilience_evaluator)
    graph.add_node("influence", evaluators.influence_evaluator)
    
    # ==================== Aggregator 노드 등록 ====================
    graph.add_node("aggregator", aggregator.aggregate)
    
    # ==================== [향후] Adversarial Validation 노드 ====================
    # TODO: Adversarial Validator 추가
    # graph.add_node("adversarial_validator", adversarial_validator_node)
    #
    # TODO: Refiner 추가  
    # graph.add_node("refiner", refiner_node)
    
    # ==================== Edge 설정 ====================
    
    # START → 6개 evaluator (병렬 실행)
    graph.set_entry_point("job_expertise")
    graph.set_entry_point("analytical")
    graph.set_entry_point("execution")
    graph.set_entry_point("relationship")
    graph.set_entry_point("resilience")
    graph.set_entry_point("influence")
    
    # 6개 evaluator → aggregator (모두 완료 후 실행)
    graph.add_edge("job_expertise", "aggregator")
    graph.add_edge("analytical", "aggregator")
    graph.add_edge("execution", "aggregator")
    graph.add_edge("relationship", "aggregator")
    graph.add_edge("resilience", "aggregator")
    graph.add_edge("influence", "aggregator")
    
    # Aggregator → END
    graph.add_edge("aggregator", END)
    
    # ==================== [향후] Adversarial Flow 추가 ====================
    # TODO: Aggregator → Adversarial Validator
    # graph.add_edge("aggregator", "adversarial_validator")
    #
    # TODO: Adversarial Validator → Refiner
    # graph.add_edge("adversarial_validator", "refiner")
    #
    # TODO: Refiner → END
    # graph.add_edge("refiner", END)
    
    # 그래프 컴파일
    compiled_graph = graph.compile()
    
    return compiled_graph


async def run_evaluation(
    llm_client: LLMClient,
    initial_state: EvaluationState
) -> EvaluationState:
    """
    평가 실행 헬퍼 함수
    
    Args:
        llm_client: LLM 클라이언트
        initial_state: 초기 상태
    
    Returns:
        최종 상태
    """
    # 그래프 생성
    graph = create_evaluation_graph(llm_client)
    
    # 시작 시간 기록
    initial_state["started_at"] = datetime.now()
    initial_state["evaluation_status"] = "evaluating"
    initial_state["execution_logs"] = []
    
    # 실행
    final_state = await graph.ainvoke(initial_state)
    
    return final_state