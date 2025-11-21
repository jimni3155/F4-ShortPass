"""
Final Integrator
Stage 3: 최종 점수 계산 및 신뢰도 평가

처리 내용:
    1. 10개 역량 가중 평균으로 최종 점수 계산
    2. 평균 Confidence V2 계산
    3. 신뢰도 레벨 판단
    4. 최종 리포트 구성
"""

from typing import Dict, List, Optional
from datetime import datetime

from .state import EvaluationState


class FinalIntegrator:
    """
    최종 통합기
    
    역할:
        - Job/Common 구분 없이 10개 역량 직접 처리
        - Confidence V2 기반 신뢰도 평가
        - Collaboration 결과 반영
    """
    
    # 신뢰도 레벨 Threshold
    RELIABILITY_THRESHOLDS = {
        "very_high": 0.85,  # 매우 높음
        "high": 0.70,       # 높음
        "medium": 0.55,     # 중간
        "low": 0.0          # 낮음
    }
    
    
    @staticmethod
    def integrate(
        aggregated_competencies: Dict[str, Dict],
        competency_weights: Dict[str, float],
        collaboration_results: Optional[List[Dict]] = None,
        low_confidence_list: Optional[List[Dict]] = None
    ) -> Dict:
        """
        최종 통합
        
        Args:
            aggregated_competencies: Aggregator에서 집계된 10개 역량
                {
                    "achievement_motivation": {
                        "overall_score": 85,
                        "confidence_v2": 0.85,
                        ...
                    },
                    ...
                }
            
            competency_weights: 10개 역량 가중치
                {
                    "achievement_motivation": 0.12,
                    "growth_potential": 0.10,
                    ...
                }
            
            collaboration_results: Collaboration Node 결과 (선택적)
            low_confidence_list: Low Confidence 목록
        
        Returns:
            final_result: 최종 리포트
                {
                    "final_score": 82.5,
                    "avg_confidence": 0.78,
                    "reliability": {
                        "level": "high",
                        "note": "..."
                    },
                    "competency_scores": [...],
                    "collaboration_summary": {...},
                    "low_confidence_summary": {...}
                }
        """
        
        print("\n[Final Integrator] 최종 통합 시작")
        
    
        # 1. Collaboration 결과 반영       
        if collaboration_results:
            print(f"  Collaboration 결과 반영: {len(collaboration_results)}건")
            aggregated_competencies = FinalIntegrator._apply_collaboration_results(
                aggregated_competencies,
                collaboration_results
            )
        else:
            print("  Collaboration 결과 없음 (스킵)")
        
        
    
        # 2. 최종 점수 계산 (가중 평균) 
        final_score, competency_scores = FinalIntegrator._calculate_final_score(
            aggregated_competencies,
            competency_weights
        )
        
        print(f"\n  최종 점수: {final_score:.1f}점")
        
        
    
        # 3. 평균 Confidence V2 계산
        avg_confidence = FinalIntegrator._calculate_avg_confidence(
            aggregated_competencies,
            competency_weights
        )
        
        print(f"  평균 Confidence V2: {avg_confidence:.2f}")
        
        
    
        # 4. 신뢰도 레벨 판단
        reliability = FinalIntegrator._determine_reliability(
            avg_confidence,
            low_confidence_list or []
        )
        
        print(f"  신뢰도 레벨: {reliability['level']}")
        print(f"  신뢰도 근거: {reliability['note']}")
        
        
    
        # 5. Collaboration 요약
        collaboration_summary = FinalIntegrator._summarize_collaboration(
            collaboration_results or []
        )
        
        
    
        # 6. Low Confidence 요약
        low_confidence_summary = FinalIntegrator._summarize_low_confidence(
            low_confidence_list or []
        )
        
        
    
        # 7. 최종 리포트 구성
        final_result = {
            "final_score": final_score,
            "avg_confidence": avg_confidence,
            
            "reliability": reliability,
            
            "competency_scores": competency_scores,
            
            "collaboration_summary": collaboration_summary,
            
            "low_confidence_summary": low_confidence_summary,
            
            "competency_details": {
                comp_name: {
                    "overall_score": comp_data["overall_score"],
                    "confidence_v2": comp_data["confidence_v2"],
                    "weight": competency_weights.get(comp_name, 0.0),
                    "weighted_contribution": comp_data["overall_score"] * competency_weights.get(comp_name, 0.0),
                    "resume_verified_count": comp_data.get("resume_verified_count", 0),
                    "segment_count": comp_data.get("segment_count", 0),
                    "strengths": comp_data.get("strengths", []),
                    "weaknesses": comp_data.get("weaknesses", [])
                }
                for comp_name, comp_data in aggregated_competencies.items()
            }
        }
        
        print("\n[Final Integrator] 최종 통합 완료")
        
        return final_result
    
    
    @staticmethod
    def _apply_collaboration_results(
        aggregated_competencies: Dict[str, Dict],
        collaboration_results: List[Dict]
    ) -> Dict[str, Dict]:
        """
        Collaboration 결과를 역량 점수에 반영
        
        Collaboration 결과 예시:
            [
                {
                    "competency": "achievement_motivation",
                    "original_score": 85,
                    "adjusted_score": 88,
                    "confidence_adjusted": 0.80,
                    "reason": "Adversarial validation"
                },
                ...
            ]
        """
        
        updated = aggregated_competencies.copy()
        
        for collab in collaboration_results:
            comp_name = collab.get("competency")
            
            if comp_name not in updated:
                continue
            
            # 점수 및 Confidence 조정
            updated[comp_name] = {
                **updated[comp_name],
                "overall_score": collab.get("adjusted_score", updated[comp_name]["overall_score"]),
                "confidence_v2": collab.get("confidence_adjusted", updated[comp_name]["confidence_v2"]),
                "collaboration_applied": True,
                "collaboration_reason": collab.get("reason")
            }
        
        return updated
    
    
    @staticmethod
    def _calculate_final_score(
        aggregated_competencies: Dict[str, Dict],
        competency_weights: Dict[str, float]
    ) -> tuple[float, List[Dict]]:
        """
        가중 평균으로 최종 점수 계산
        
        Returns:
            (final_score, competency_scores)
            
            competency_scores: 역량별 기여도
                [
                    {
                        "competency": "achievement_motivation",
                        "score": 85,
                        "weight": 0.12,
                        "contribution": 10.2
                    },
                    ...
                ]
        """
        
        total_weighted_score = 0.0
        total_weight = 0.0
        competency_scores = []
        
        for comp_name, comp_data in aggregated_competencies.items():
            score = comp_data["overall_score"]
            weight = competency_weights.get(comp_name, 0.0)
            
            contribution = score * weight
            
            total_weighted_score += contribution
            total_weight += weight
            
            competency_scores.append({
                "competency": comp_name,
                "score": score,
                "weight": weight,
                "contribution": round(contribution, 2),
                "confidence_v2": comp_data["confidence_v2"]
            })
        
        # 가중치 합이 1.0이 아닐 경우 정규화
        if total_weight > 0:
            final_score = total_weighted_score / total_weight
        else:
            final_score = 0.0
        
        # 정렬 (기여도 높은 순)
        competency_scores.sort(key=lambda x: x["contribution"], reverse=True)
        
        return round(final_score, 1), competency_scores
    
    
    @staticmethod
    def _calculate_avg_confidence(
        aggregated_competencies: Dict[str, Dict],
        competency_weights: Dict[str, float]
    ) -> float:
        """
        가중 평균 Confidence V2 계산
        """
        
        total_weighted_conf = 0.0
        total_weight = 0.0
        
        for comp_name, comp_data in aggregated_competencies.items():
            conf_v2 = comp_data["confidence_v2"]
            weight = competency_weights.get(comp_name, 0.0)
            
            total_weighted_conf += conf_v2 * weight
            total_weight += weight
        
        if total_weight > 0:
            avg_conf = total_weighted_conf / total_weight
        else:
            avg_conf = 0.5
        
        return round(avg_conf, 2)
    
    
    @staticmethod
    def _determine_reliability(
        avg_confidence: float,
        low_confidence_list: List[Dict]
    ) -> Dict:
        """
        신뢰도 레벨 판단
        
        Returns:
            {
                "level": "high",  # "very_high", "high", "medium", "low"
                "note": "평균 Confidence V2가 높고 (0.78), Low Confidence 역량 없음"
            }
        """
        
        # 레벨 결정
        if avg_confidence >= FinalIntegrator.RELIABILITY_THRESHOLDS["very_high"]:
            level = "very_high"
            level_kr = "매우 높음"
        elif avg_confidence >= FinalIntegrator.RELIABILITY_THRESHOLDS["high"]:
            level = "high"
            level_kr = "높음"
        elif avg_confidence >= FinalIntegrator.RELIABILITY_THRESHOLDS["medium"]:
            level = "medium"
            level_kr = "중간"
        else:
            level = "low"
            level_kr = "낮음"
        
        # 근거 설명
        note_parts = [
            f"평균 Confidence V2: {avg_confidence:.2f}"
        ]
        
        if low_confidence_list:
            note_parts.append(f"Low Confidence 역량: {len(low_confidence_list)}개")
            for item in low_confidence_list:
                note_parts.append(f"  - {item['competency']}: {item['confidence_v2']:.2f}")
        else:
            note_parts.append("모든 역량이 신뢰도 기준 충족")
        
        note = " | ".join(note_parts)
        
        return {
            "level": level,
            "level_display": level_kr,
            "avg_confidence": avg_confidence,
            "note": note
        }
    
    
    @staticmethod
    def _summarize_collaboration(
        collaboration_results: List[Dict]
    ) -> Dict:
        """
        Collaboration 요약
        
        Returns:
            {
                "total_collaborations": 3,
                "competencies_adjusted": ["achievement_motivation", ...],
                "adjustments": [...]
            }
        """
        
        if not collaboration_results:
            return {
                "total_collaborations": 0,
                "competencies_adjusted": [],
                "adjustments": []
            }
        
        competencies_adjusted = [c["competency"] for c in collaboration_results]
        
        return {
            "total_collaborations": len(collaboration_results),
            "competencies_adjusted": competencies_adjusted,
            "adjustments": collaboration_results
        }
    
    
    @staticmethod
    def _summarize_low_confidence(
        low_confidence_list: List[Dict]
    ) -> Dict:
        """
        Low Confidence 요약
        
        Returns:
            {
                "total_low_confidence": 2,
                "competencies": ["growth_potential", "organizational_fit"],
                "details": [...]
            }
        """
        
        if not low_confidence_list:
            return {
                "total_low_confidence": 0,
                "competencies": [],
                "details": []
            }
        
        competencies = [item["competency"] for item in low_confidence_list]
        
        return {
            "total_low_confidence": len(low_confidence_list),
            "competencies": competencies,
            "details": low_confidence_list
        }


async def final_integration_node(state: EvaluationState) -> Dict:
    """
    Stage 3: Final Integration Node
    
    Aggregator 결과와 (선택적) Collaboration 결과를 최종 리포트로 통합합니다.
    """
    start_time = datetime.now()

    print("\n" + "=" * 60)
    print("[Stage 3] Final Integration 시작")
    print("=" * 60)

    aggregated_competencies = state.get("aggregated_competencies", {})
    competency_weights = state.get("competency_weights", {})
    collaboration_results = state.get("collaboration_results", [])
    low_confidence_list = state.get("low_confidence_list", [])

    final_result = FinalIntegrator.integrate(
        aggregated_competencies=aggregated_competencies,
        competency_weights=competency_weights,
        collaboration_results=collaboration_results,
        low_confidence_list=low_confidence_list
    )

    duration = (datetime.now() - start_time).total_seconds()

    execution_log = {
        "node": "final_integration",
        "duration_seconds": round(duration, 2),
        "timestamp": datetime.now().isoformat(),
        "status": "success"
    }

    return {
        "final_score": final_result.get("final_score"),
        "avg_confidence": final_result.get("avg_confidence"),
        "final_reliability": final_result.get("reliability", {}).get("level"),
        "reliability_note": final_result.get("reliability", {}).get("note"),
        "final_result": final_result,
        "execution_logs": state.get("execution_logs", []) + [execution_log]
    }
