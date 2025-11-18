"""
Confidence Validator
낮은 신뢰도 역량 검증
"""

from typing import Dict, List


class ConfidenceValidator:
    """신뢰도 검증"""
    
    @staticmethod
    def validate(
        job_aggregation: Dict,
        common_aggregation: Dict,
        threshold: float = 0.7
    ) -> Dict:
        """
        낮은 신뢰도 역량 검증
        
        Args:
            job_aggregation: Job 통합 결과
            common_aggregation: Common 통합 결과
            threshold: 신뢰도 임계값 (기본 0.7)
        
        Returns:
            검증 결과
                {
                    "low_confidence_competencies": [...],
                    "validation_notes": "...",
                    "requires_revaluation": bool
                }
        """
        
        # 1. 낮은 신뢰도 역량 수집
        all_low_confidence = []
        all_low_confidence.extend(job_aggregation.get("low_confidence_competencies", []))
        all_low_confidence.extend(common_aggregation.get("low_confidence_competencies", []))
        
        # 2. 검증 노트 생성
        if len(all_low_confidence) == 0:
            validation_notes = "모든 역량 평가의 신뢰도가 충분합니다."
            requires_revaluation = False
        elif len(all_low_confidence) <= 2:
            validation_notes = (
                f"{len(all_low_confidence)}개 역량의 신뢰도가 낮습니다 "
                f"({', '.join(all_low_confidence)}). "
                f"참고용으로 사용 가능하나, 추가 검증 권장."
            )
            requires_revaluation = False
        else:
            validation_notes = (
                f"{len(all_low_confidence)}개 역량의 신뢰도가 낮습니다 "
                f"({', '.join(all_low_confidence)}). "
                f"평가 신뢰성이 낮아 재평가 필요."
            )
            requires_revaluation = True
        
        return {
            "low_confidence_competencies": list(set(all_low_confidence)),  # 중복 제거
            "validation_notes": validation_notes,
            "requires_revaluation": requires_revaluation
        }