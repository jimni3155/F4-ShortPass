"""
Phase 4 Node: 최종 통합 (final_integration_node)
개별 역량 점수는 원본 유지하되, 최종 점수와 신뢰도만 계산

처리 내용:
1. 10개 역량의 평균 Confidence 계산
2. Confidence 기반 신뢰도 레벨 판단
3. Job/Common 비율 적용하여 최종 점수 계산
4. 최종 결과 구성

예상 시간: ~0.5초
"""

from typing import Dict
from datetime import datetime
from ..aggregators.final_integrator import FinalIntegrator


async def final_integration_node(state: Dict) -> Dict:
    """
    Phase 4: 최종 통합 Node
    
    Args:
        state: EvaluationState
    
    Returns:
        업데이트할 State 필드
            - final_score
            - avg_confidence
            - final_reliability
            - reliability_note
            - final_result
            - completed_at
    """
    
    start_time = datetime.now()
    
    print("\n" + "="*60)
    print("[Phase 4] 최종 통합 시작")
    print("="*60)
    
    
    # 1. FinalIntegrator 사용
    final_result = FinalIntegrator.integrate(
        job_aggregation=state["job_aggregation_result"],
        common_aggregation=state["common_aggregation_result"],
        mediation_results=state.get("mediation_results", []),
        adversarial_results=state.get("adversarial_results", []),
        collaboration_count=state.get("collaboration_count", 0),
        job_common_ratio=state["job_common_ratio"]
    )
    
    
    # 2. 결과 출력  
    print(f"\n✓ 최종 점수 계산 완료")
    print(f"  - Job 점수: {final_result['job_score']}점 (가중치 {final_result['job_common_ratio']['job']*100:.0f}%)")
    print(f"  - Common 점수: {final_result['common_score']}점 (가중치 {final_result['job_common_ratio']['common']*100:.0f}%)")
    print(f"  → 최종 점수: {final_result['final_score']}점")
    
    print(f"\n✓ 신뢰도 평가 완료")
    print(f"  - 평균 Confidence: {final_result['avg_confidence']}")
    print(f"  - 신뢰도 레벨: {final_result['reliability']['level']}")
    print(f"  - 협업 조정: {final_result['adjustments_summary']['total_adjustments']}건")
    
    
    # 3. 성능 로깅
    duration = (datetime.now() - start_time).total_seconds()
    
    execution_log = {
        "phase": "phase_4",
        "node": "final_integration",
        "duration_seconds": round(duration, 2),
        "final_score": final_result['final_score'],
        "avg_confidence": final_result['avg_confidence'],
        "reliability": final_result['reliability']['level'],
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"\n  Phase 4 완료: {duration:.2f}초")
    print("="*60)
    
    
    # 4. State 업데이트
    return {
        "final_score": final_result["final_score"],
        "avg_confidence": final_result["avg_confidence"],
        "final_reliability": final_result["reliability"]["level"],
        "reliability_note": final_result["reliability"]["note"],
        "final_result": final_result,
        "completed_at": datetime.now(),
        "execution_logs": state.get("execution_logs", []) + [execution_log]
    }