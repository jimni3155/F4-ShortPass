"""
Competency Agent (OpenAI 직접 호출)
10개 역량 병렬 평가
"""

import asyncio
from asyncio import Semaphore
import json
import hashlib
from typing import Dict
from datetime import datetime
from openai import AsyncOpenAI


class CompetencyAgent:
    """역량 평가 Agent"""
    
    def __init__(self, openai_client: AsyncOpenAI, max_concurrent: int = 5):
        """
        Args:
            openai_client: OpenAI AsyncClient
            max_concurrent: 동시 실행 최대 개수
        """
        self.client = openai_client
        self.model = "gpt-4o"
        self.semaphore = Semaphore(max_concurrent)
        self.cache = {}
    
    def _get_cache_key(self, competency_name: str, transcript: Dict) -> str:
        """캐시 키 생성"""
        transcript_str = json.dumps(transcript, sort_keys=True, ensure_ascii=False)
        transcript_hash = hashlib.md5(transcript_str.encode()).hexdigest()
        return f"{competency_name}:{transcript_hash}"
    
    async def evaluate(
        self, 
        competency_name: str,
        competency_display_name: str,
        competency_category: str,
        prompt: str,
        transcript: Dict
    ) -> Dict:
        """역량 평가 실행"""
        
        # 캐시 확인
        cache_key = self._get_cache_key(competency_name, transcript)
        if cache_key in self.cache:
            print(f"[캐시 히트] {competency_name}")
            return self.cache[cache_key]
        
        # Rate Limiting
        async with self.semaphore:
            print(f"[평가 시작] {competency_name}")
            
            try:
                # OpenAI 호출 (재시도 포함)
                for attempt in range(3):
                    try:
                        response = await self.client.chat.completions.create(
                            model=self.model,
                            messages=[
                                {
                                    "role": "system",
                                    "content": "You are an expert HR evaluator. Respond with ONLY valid JSON."
                                },
                                {
                                    "role": "user",
                                    "content": prompt
                                }
                            ],
                            temperature=0.0,
                            max_tokens=4000,
                            response_format={"type": "json_object"}
                        )
                        
                        content = response.choices[0].message.content.strip()
                        
                        # 마크다운 제거
                        if content.startswith("```"):
                            content = content.split("```")[1]
                            if content.startswith("json"):
                                content = content[4:]
                        content = content.strip()
                        
                        # JSON 파싱
                        result = json.loads(content)
                        
                        # 메타 정보 추가
                        result["competency_name"] = competency_name
                        result["competency_display_name"] = competency_display_name
                        result["competency_category"] = competency_category
                        result["evaluated_at"] = datetime.now().isoformat()
                        
                        # 캐싱
                        self.cache[cache_key] = result
                        
                        print(f"[평가 완료] {competency_name}: {result.get('overall_score', 0)}점")
                        
                        return result
                        
                    except (json.JSONDecodeError, Exception) as e:
                        if attempt < 2:
                            print(f"[재시도 {attempt+1}/3] {competency_name}: {e}")
                            await asyncio.sleep(1)
                        else:
                            raise
                            
            except Exception as e:
                raise RuntimeError(f"[{competency_name}] 평가 실패: {e}")


async def evaluate_all_competencies(
    agent: CompetencyAgent,
    transcript: Dict,
    prompts: Dict[str, str]
) -> Dict[str, Dict]:
    """
    10개 역량 배치 평가
    
    Args:
        agent: CompetencyAgent 인스턴스
        transcript: Interview Transcript JSON
        prompts: 역량별 프롬프트 Dict
            {
                "achievement_motivation": "...",
                "growth_potential": "...",
                ...
            }
    
    Returns:
        역량별 평가 결과
            {
                "achievement_motivation": {...},
                "growth_potential": {...},
                ...
            }
    """
    
    print("=" * 60)
    print("10개 역량 배치 평가 시작")
    print("=" * 60)
    
   
    # 10개 역량 설정 (최종 버전)
    competency_configs = [
        # Common Competencies (5개) - 프롬프트 파일명과 정확히 일치
        ("achievement_motivation", "성취/동기 역량", "common"),
        ("growth_potential", "성장 잠재력", "common"),
        ("interpersonal_skill", "대인관계 역량", "common"), 
        ("organizational_fit", "조직 적합성", "common"),
        ("problem_solving", "문제해결력", "common"),
        
        # Job Competencies (5개) - 프롬프트 파일명과 정확히 일치
        ("customer_journey_marketing", "고객 여정 설계 및 VMD·마케팅 통합 전략", "job"),
        ("md_data_analysis", "매출·트렌드 데이터 분석 및 상품 기획", "job"),
        ("seasonal_strategy_kpi", "시즌 전략 수립 및 비즈니스 문제해결", "job"),
        ("stakeholder_collaboration", "유관부서 협업 및 이해관계자 협상", "job"),
        ("value_chain_optimization", "소싱·생산·유통 밸류체인 최적화", "job"),
    ]
    
   
    # 병렬 평가 실행
    tasks = [
        agent.evaluate(name, display, category, prompts[name], transcript)
        for name, display, category in competency_configs
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    print("=" * 60)
    print("배치 평가 완료")
    print("=" * 60)
    
   
    # 결과 매핑
    result_dict = {}
    for (name, _, _), result in zip(competency_configs, results):
        if isinstance(result, Exception):
            print(f"[오류] {name}: {str(result)}")
            result_dict[name] = {
                "error": str(result),
                "overall_score": 0,
                "confidence": {
                    "overall_confidence": 0.3
                }
            }
        else:
            result_dict[name] = result
    
    return result_dict