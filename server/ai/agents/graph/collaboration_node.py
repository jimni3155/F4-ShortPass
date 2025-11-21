"""
Phase 3 Node: Targeted Collaboration (collaboration_node)
문제가 있는 역량/segment만 선택적으로 협업 처리

처리 내용:
1. Evidence 충돌 중재 (최대 3개)
2. Low Confidence 재평가 (최대 5개)
3. 병렬 실행으로 시간 단축

예상 시간: ~10-15초 (병렬 처리)
"""

import sys
import asyncio
from pathlib import Path
from typing import Dict
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))
from collaborators.evidence_mediator import EvidenceMediator
from collaborators.adversarial_validator import AdversarialValidator


async def collaboration_node(state: Dict) -> Dict:
    """
    Phase 3: Targeted Collaboration Node
    
    Args:
        state: EvaluationState
    
    Returns:
        업데이트할 State 필드
            - mediation_results
            - adversarial_results
            - collaboration_count
    """
    
    start_time = datetime.now()
    
    print("\n" + "="*60)
    print("[Phase 3] Targeted Collaboration 시작")
    print("="*60)
    
    
    # 1. 입력 데이터 준비
    evidence_conflicts = state["evidence_conflicts"]
    low_confidence_list = state["low_confidence_list"]
    
    print(f"✓ Evidence 충돌: {len(evidence_conflicts)}건")
    print(f"✓ Low Confidence: {len(low_confidence_list)}개")
    
    # 10개 역량 결과 수집
    all_results = {
        "problem_solving": state["problem_solving_result"],
        "organizational_fit": state["organizational_fit_result"],
        "growth_potential": state["growth_potential_result"],
        "interpersonal_skills": state["interpersonal_skills_result"],
        "achievement_motivation": state["achievement_motivation_result"],
        "structured_thinking": state["structured_thinking_result"],
        "business_documentation": state["business_documentation_result"],
        "financial_literacy": state["financial_literacy_result"],
        "industry_learning": state["industry_learning_result"],
        "stakeholder_management": state["stakeholder_management_result"],
    }
    all_results = {k: v for k, v in all_results.items() if v is not None}
    
    transcript = state["transcript"]
    openai_client = state["openai_client"]
    
    
    # 2. Collaborator 초기화 
    mediator = EvidenceMediator(openai_client)
    validator = AdversarialValidator(openai_client)
    
    
    # 3. 병렬 실행
    print("\n[3-1] Evidence 충돌 중재 + Low Confidence 재평가 (병렬 실행)...")
    
    # 두 작업을 동시에 실행
    mediation_task = mediator.mediate_conflicts(
        evidence_conflicts,
        all_results,
        transcript,
        max_mediations=3
    ) if evidence_conflicts else asyncio.sleep(0)
    
    validation_task = validator.validate_low_confidence(
        low_confidence_list,
        all_results,
        max_validations=5
    ) if low_confidence_list else asyncio.sleep(0)
    
    # 병렬 실행
    mediation_results, adversarial_results = await asyncio.gather(
        mediation_task,
        validation_task,
        return_exceptions=True
    )

    # Exception 처리
    if isinstance(mediation_results, Exception):
        print(f"⚠️  Evidence 중재 실패: {mediation_results}")
        mediation_results = []
    elif mediation_results in (0, None):  # asyncio.sleep(0) or None
        mediation_results = []
    
    if isinstance(adversarial_results, Exception):
        print(f"⚠️  Adversarial 재평가 실패: {adversarial_results}")
        adversarial_results = []
    elif adversarial_results in (0, None):  # asyncio.sleep(0) or None
        adversarial_results = []
    
    
    # 4. 결과 요약
    collaboration_count = len(mediation_results) + len(adversarial_results)
    
    print(f"\n✓ Evidence 중재 완료: {len(mediation_results)}건")
    if mediation_results:
        for result in mediation_results:
            segment_id = result.get("segment_id")
            primary = result.get("primary_competency")
            print(f"  - Segment {segment_id}: Primary={primary}")
    
    print(f"\n✓ Adversarial 재평가 완료: {len(adversarial_results)}개")
    if adversarial_results:
        for result in adversarial_results:
            comp = result.get("competency")
            orig = result.get("original_score")
            adj = result.get("adjusted_score")
            conf = result.get("confidence_adjusted")
            print(f"  - {comp}: {orig}점 → {adj}점 (Confidence: {conf:.2f})")
    
    
    # 5. 성능 로깅
    duration = (datetime.now() - start_time).total_seconds()
   
    execution_log = {
        "phase": "phase_3",
        "node": "collaboration",
        "duration_seconds": round(duration, 2),
        "mediations_done": len(mediation_results),
        "validations_done": len(adversarial_results),
        "total_collaborations": collaboration_count,
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"\n  Phase 3 완료: {duration:.2f}초")
    print("="*60)
    
    
    # 6. State 업데이트
    return {
        "mediation_results": mediation_results,
        "adversarial_results": adversarial_results,
        "collaboration_count": collaboration_count,
        "execution_logs": state["execution_logs"] + [execution_log]
    }
