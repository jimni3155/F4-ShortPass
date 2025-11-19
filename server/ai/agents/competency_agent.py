"""
Competency Agent (OpenAI 직접 호출)
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
    """10개 역량 배치 평가"""
    
    print("=" * 60)
    print("10개 역량 배치 평가 시작")
    print("=" * 60)
    
    competency_configs = [
        ("problem_solving", "문제해결력", "common"),
        ("organizational_fit", "조직 적합성", "common"),
        ("growth_potential", "성장 잠재력", "common"),
        ("interpersonal_skills", "대인관계 역량", "common"),
        ("achievement_motivation", "성취/동기 역량", "common"),
        ("structured_thinking", "구조화 사고", "job"),
        ("business_documentation", "전략 문서화", "job"),
        ("financial_literacy", "재무 경영 감각", "job"),
        ("industry_learning", "산업 학습 민첩성", "job"),
        ("stakeholder_management", "이해관계자 관리", "job"),
    ]
    
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
            result_dict[name] = {"error": str(result), "overall_score": 0}
        else:
            result_dict[name] = result
    
    return result_dict