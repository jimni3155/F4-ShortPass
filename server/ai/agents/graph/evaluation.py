"""
LangGraph Evaluation Graph
Phase 1 → Phase 2 → Phase 3 (조건부) → Phase 4

플로우:
START → Phase 1 (배치 평가 + 통합 + 검증) 
      → Phase 2 (문제 탐지)
      → [조건부 분기]
          ├─ 문제 있음 → Phase 3 (협업) → Phase 4 (최종 통합)
          └─ 문제 없음 → Phase 4 (최종 통합)
"""

from langgraph.graph import StateGraph, END
from .state import EvaluationState
from .nodes import (
    batch_evaluation_node,
    job_aggregator_node,
    common_aggregator_node,
    confidence_validator_node,
)
from .detect_issues_node import detect_issues_node
from .collaboration_node import collaboration_node
from .final_integration_node import final_integration_node


def should_collaborate(state: EvaluationState) -> str:
    """
    Phase 2 후 협업 필요 여부 판단
    
    Returns:
        "collaboration": Phase 3로 진행
        "final_integration": Phase 4로 바로 진행
    """
    requires_collaboration = state.get("requires_collaboration", False)
    
    if requires_collaboration:
        return "collaboration"
    else:
        return "final_integration"


def create_evaluation_graph():
    """
    평가 그래프 생성
    
    플로우:
    Phase 1: 배치 평가 (10개 병렬) → Job/Common 통합 → 검증
    Phase 2: 문제 탐지 (Evidence 충돌 + Low Confidence)
    Phase 3: 협업 (조건부)
    Phase 4: 최종 통합
    """
    
    graph = StateGraph(EvaluationState)
    
    
    # 1. Node 등록
    # Phase 1
    graph.add_node("batch_evaluation", batch_evaluation_node)
    graph.add_node("job_aggregator", job_aggregator_node)
    graph.add_node("common_aggregator", common_aggregator_node)
    graph.add_node("confidence_validator", confidence_validator_node)
    
    # Phase 2
    graph.add_node("detect_issues", detect_issues_node)
    
    # Phase 3
    graph.add_node("collaboration", collaboration_node)
    
    # Phase 4
    graph.add_node("final_integration", final_integration_node)
    
    
    # 2. Phase 1 플로우
    # Entry Point
    graph.set_entry_point("batch_evaluation")
    
    # 배치 평가 → Job/Common 통합 (병렬)
    graph.add_edge("batch_evaluation", "job_aggregator")
    graph.add_edge("batch_evaluation", "common_aggregator")
    
    # Job/Common 통합 → 검증
    graph.add_edge("job_aggregator", "confidence_validator")
    graph.add_edge("common_aggregator", "confidence_validator")
    
    
    # 3. Phase 1 → Phase 2
    # 검증 → 문제 탐지
    graph.add_edge("confidence_validator", "detect_issues")
    
    
    # 4. Phase 2 → Phase 3 (조건부) or Phase 4
    # 조건부 분기
    graph.add_conditional_edges(
        "detect_issues",
        should_collaborate,
        {
            "collaboration": "collaboration",
            "final_integration": "final_integration"
        }
    )
    
    
    # 5. Phase 3 → Phase 4
    # 협업 → 최종 통합
    graph.add_edge("collaboration", "final_integration")
    
    
    # 6. Phase 4 → END
    # 최종 통합 → 종료
    graph.add_edge("final_integration", END)
    
    return graph.compile()