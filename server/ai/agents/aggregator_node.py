# ai/agents/aggregator_node.py
"""
6개 evaluator 결과를 통합하고 최종 판단을 내리는 노드
"""

import json
from typing import Dict, Any
from datetime import datetime

from ai.utils.llm_client import LLMClient
from ai.agents.state import EvaluationState


AGGREGATOR_PROMPT = """당신은 6개 역량 평가 결과를 통합하여 최종 채용 판단을 내리는 시니어 면접관입니다.

<평가_결과>
Job Expertise: {job_expertise_score}점
- Reasoning: {job_expertise_reasoning}

Analytical: {analytical_score}점  
- Reasoning: {analytical_reasoning}

Execution: {execution_score}점
- Reasoning: {execution_reasoning}

Relationship: {relationship_score}점
- Reasoning: {relationship_reasoning}

Resilience: {resilience_score}점
- Reasoning: {resilience_reasoning}

Influence: {influence_score}점
- Reasoning: {influence_reasoning}
</평가_결과>

<역량별_가중치>
{competency_weights}
</역량별_가중치>

<임무>
1. 가중치를 적용하여 최종 점수 계산
2. 종합 피드백 작성 (overall_feedback)
3. 핵심 인사이트 도출 (key_insights)
4. 채용 추천 결정 (hiring_recommendation)
5. JD 요구사항 충족도 평가 (job_requirement_fit_score)
6. 온보딩 예측 (expected_onboarding_duration)
</임무>

<출력_형식>
오직 유효한 JSON만 반환하세요.

{{
  "weighted_total_score": 82.5,
  "raw_total_score": 80.3,
  "aggregation_reasoning": "6개 역량을 종합한 판단...",
  
  "overall_feedback": "지원자는 기술 역량이 탄탄하며...",
  
  "key_insights": {{
    "top_3_strengths": ["강점1", "강점2", "강점3"],
    "top_3_concerns": ["우려1", "우려2", "우려3"],
    "job_requirement_alignment": {{
      "overall_fit": "high",
      "requirements_met": ["요구사항1", "요구사항2"],
      "requirements_missing": ["부족한 부분1"],
      "exceeds_requirements": ["초과 달성 항목1"]
    }},
    "readiness_for_role": {{
      "immediate_contribution": "high",
      "growth_areas": [
        {{
          "area": "Kubernetes",
          "current_level": "beginner",
          "target_level": "intermediate",
          "estimated_timeline": "3개월"
        }}
      ]
    }},
    "risk_factors": [
      {{
        "risk": "스트레스 관리 능력 부족",
        "severity": "medium",
        "mitigation": "멘토링 및 워크로드 모니터링"
      }}
    ]
  }},
  
  "hiring_recommendation": "hire",
  "recommendation_reasoning": "필수 요구사항 충족...",
  
  "job_requirement_fit_score": 85.0,
  "fit_analysis": "JD 필수 기술 90% 충족...",
  
  "expected_onboarding_duration": "1-3months",
  "onboarding_support_needed": ["Docker 교육", "도메인 지식 학습"]
}}
</출력_형식>
"""


class AggregatorNode:
    """
    6개 evaluator 결과를 통합하는 노드
    """
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
    
    async def aggregate(self, state: EvaluationState) -> Dict[str, Any]:
        """
        6개 evaluator 결과 통합
        """
        start_time = datetime.now()
        
        try:
            # 6개 결과 체크
            results = {
                "job_expertise": state.get("job_expertise_result"),
                "analytical": state.get("analytical_result"),
                "execution": state.get("execution_result"),
                "relationship": state.get("relationship_result"),
                "resilience": state.get("resilience_result"),
                "influence": state.get("influence_result"),
            }
            
            # 누락된 결과 확인
            missing = [k for k, v in results.items() if v is None]
            if missing:
                raise ValueError(f"Missing evaluation results: {missing}")
            
            # 프롬프트 컨텍스트 준비
            context = {
                "job_expertise_score": results["job_expertise"]["score"],
                "job_expertise_reasoning": results["job_expertise"]["reasoning"],
                "analytical_score": results["analytical"]["score"],
                "analytical_reasoning": results["analytical"]["reasoning"],
                "execution_score": results["execution"]["score"],
                "execution_reasoning": results["execution"]["reasoning"],
                "relationship_score": results["relationship"]["score"],
                "relationship_reasoning": results["relationship"]["reasoning"],
                "resilience_score": results["resilience"]["score"],
                "resilience_reasoning": results["resilience"]["reasoning"],
                "influence_score": results["influence"]["score"],
                "influence_reasoning": results["influence"]["reasoning"],
                "competency_weights": json.dumps(
                    state["competency_weights"], 
                    ensure_ascii=False, 
                    indent=2
                ),
            }
            
            # 프롬프트 생성
            prompt = AGGREGATOR_PROMPT.format(**context)
            
            # LLM 호출
            response = await self.llm_client.ainvoke(prompt)
            
            # JSON 파싱
            response_text = response.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            aggregated = json.loads(response_text)
            
            # 실행 시간 기록
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "aggregated_scores": {
                    "job_expertise": results["job_expertise"]["score"],
                    "analytical": results["analytical"]["score"],
                    "execution": results["execution"]["score"],
                    "relationship": results["relationship"]["score"],
                    "resilience": results["resilience"]["score"],
                    "influence": results["influence"]["score"],
                },
                "overall_feedback": aggregated["overall_feedback"],
                "key_insights": aggregated["key_insights"],
                "hiring_recommendation": aggregated["hiring_recommendation"],
                "recommendation_reasoning": aggregated["recommendation_reasoning"],
                "job_requirement_fit_score": aggregated["job_requirement_fit_score"],
                "fit_analysis": aggregated["fit_analysis"],
                "expected_onboarding_duration": aggregated["expected_onboarding_duration"],
                "onboarding_support_needed": aggregated["onboarding_support_needed"],
                "evaluation_status": "completed",
                "completed_at": datetime.now(),
                "execution_logs": [
                    {
                        "node": "aggregator",
                        "execution_time": execution_time,
                        "error": None,
                        "timestamp": datetime.now().isoformat()
                    }
                ]
            }
            
        except Exception as e:
            return {
                "evaluation_status": "failed",
                "error_message": f"Aggregation failed: {str(e)}",
                "execution_logs": [
                    {
                        "node": "aggregator",
                        "execution_time": (datetime.now() - start_time).total_seconds(),
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
                ]
            }