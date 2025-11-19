"""
간단한 테스트 (API 서버 없이 직접 호출)
"""

import asyncio
import json
from services.evaluation.evaluation_service import EvaluationService


async def test_direct_evaluation():
    """API 없이 직접 서비스 호출 테스트"""
    
    # 테스트 데이터
    transcript = {
        "metadata": {
            "interview_id": 1,
            "applicant_id": 100,
            "job_id": 200,
            "duration_sec": 180
        },
        "segments": [
            {
                "segment_id": 1,
                "segment_order": 1,
                "question_text": "자기소개를 부탁드립니다.",
                "answer_text": "안녕하세요. 저는 데이터 분석에 관심이 많습니다. 대학에서 통계학을 전공했고, 최근에는 파이썬으로 데이터를 분석하는 프로젝트를 진행했습니다.",
                "answer_duration_sec": 60,
                "char_index_start": 0,
                "char_index_end": 100
            },
            {
                "segment_id": 2,
                "segment_order": 2,
                "question_text": "가장 도전적이었던 프로젝트는?",
                "answer_text": "인턴십에서 6개월치 마케팅 데이터를 분석했습니다. 데이터가 복잡했지만 피벗 테이블로 정리하고 ROI를 계산해서 개선 방안을 제시했습니다.",
                "answer_duration_sec": 60,
                "char_index_start": 0,
                "char_index_end": 120
            },
            {
                "segment_id": 3,
                "segment_order": 3,
                "question_text": "팀에서 갈등을 해결한 경험은?",
                "answer_text": "조별 과제에서 의견이 갈렸을 때, 각자의 의견을 표로 정리해서 장단점을 비교했고, 결국 합의점을 찾았습니다.",
                "answer_duration_sec": 60,
                "char_index_start": 0,
                "char_index_end": 100
            }
        ]
    }
    
    print("\n" + "="*60)
    print("직접 평가 서비스 테스트")
    print("="*60 + "\n")
    
    # 서비스 초기화
    service = EvaluationService()
    
    print(" 평가 시작...")
    
    try:
        # 평가 실행
        result = await service.evaluate_interview(
            interview_id=1,
            applicant_id=100,
            job_id=200,
            transcript=transcript,
            job_weights={
                "structured_thinking": 0.25,
                "business_documentation": 0.20,
                "financial_literacy": 0.20,
                "industry_learning": 0.20,
                "stakeholder_management": 0.15
            },
            common_weights={
                "problem_solving": 0.25,
                "organizational_fit": 0.20,
                "growth_potential": 0.20,
                "interpersonal_skills": 0.20,
                "achievement_motivation": 0.15
            }
        )
        
        print("\n✅ 평가 완료!\n")
        
        # 결과 출력
        print("="*60)
        print("Job 역량 평가")
        print("="*60)
        
        job_agg = result["job_aggregation"]
        print(f"\n종합 점수: {job_agg['overall_job_score']}점\n")
        
        for comp in ["structured_thinking", "business_documentation", 
                     "financial_literacy", "industry_learning", "stakeholder_management"]:
            comp_data = job_agg.get(comp)
            if comp_data:
                print(f"  - {comp}: {comp_data.get('overall_score', 0)}점")
        
        print(f"\n{'='*60}")
        print("Common 역량 평가")
        print("="*60)
        
        common_agg = result["common_aggregation"]
        print(f"\n종합 점수: {common_agg['overall_common_score']}점\n")
        
        for comp in ["problem_solving", "organizational_fit", 
                     "growth_potential", "interpersonal_skills", "achievement_motivation"]:
            comp_data = common_agg.get(comp)
            if comp_data:
                print(f"  - {comp}: {comp_data.get('overall_score', 0)}점")
        
        print(f"\n{'='*60}")
        print("검증 결과")
        print("="*60)
        
        validation = result["validation"]
        print(f"\n신뢰도 낮은 역량: {validation['low_confidence_competencies']}")
        print(f"검증 노트: {validation['validation_notes']}")
        print(f"재평가 필요: {validation['requires_revaluation']}\n")
        
        print("="*60)
        print("테스트 완료")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_direct_evaluation())