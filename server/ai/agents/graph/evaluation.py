# server/ai/agents/graph/evaluation.py
"""
LangGraph Evaluation Graph
배치 평가 → Job/Common 통합 → 검증
"""
from langgraph.graph import StateGraph, END
from .state import EvaluationState
from .nodes import (
    batch_evaluation_node,
    job_aggregator_node,
    common_aggregator_node,
    confidence_validator_node
)


def create_evaluation_graph():
    """
    평가 그래프 생성
    
    플로우:
    START → 배치 평가 (10개 병렬) → Job 통합 + Common 통합 → 검증 → END
    """
    
    graph = StateGraph(EvaluationState)
    
    # ============================================
    # 1. Node 등록
    # ============================================
    
    graph.add_node("batch_evaluation", batch_evaluation_node)
    graph.add_node("job_aggregator", job_aggregator_node)
    graph.add_node("common_aggregator", common_aggregator_node)
    graph.add_node("confidence_validator", confidence_validator_node)
    
    # ============================================
    # 2. 플로우 정의
    # ============================================
    
    # Entry Point
    graph.set_entry_point("batch_evaluation")
    
    # 배치 평가 → Job/Common 통합 (병렬)
    graph.add_edge("batch_evaluation", "job_aggregator")
    graph.add_edge("batch_evaluation", "common_aggregator")
    
    # Job/Common 통합 → 검증
    graph.add_edge("job_aggregator", "confidence_validator")
    graph.add_edge("common_aggregator", "confidence_validator")
    
    # 검증 → END
    graph.add_edge("confidence_validator", END)
    
    return graph.compile()


# 그래프 시각화 (참고용)
"""
START
  │
  └─→ [배치 평가] ← 10개 Agent asyncio.gather
        │
        ├─→ [Job 통합]
        │      │
        │      └─→ [검증] → END
        │            ↑
        └─→ [Common 통합]
               │
               └──────┘
"""


# 사용 예시
# async def example():
#     from datetime import datetime
#     
#     # 초기 상태
#     initial_state = {
#         "interview_id": 123,
#         "applicant_id": 456,
#         "job_id": 789,
#         "transcript": {...},
#         "job_weights": {
#             "structured_thinking": 0.25,
#             "business_documentation": 0.20,
#             ...
#         },
#         "common_weights": {
#             "problem_solving": 0.25,
#             ...
#         },
#         "started_at": datetime.now(),
#         "errors": []
#     }
#     
#     # 그래프 실행
#     graph = create_evaluation_graph()
#     result = await graph.ainvoke(initial_state)
#     
#     print(result["job_aggregation_result"])
#     print(result["common_aggregation_result"])