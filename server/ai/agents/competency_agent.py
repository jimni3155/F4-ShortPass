"""
Competency Agent (수정 버전)
10개 역량 병렬 평가

수정 내용:
    1. LLM 응답 후 필수 필드 검증
    2. key_observations 누락 시 자동 생성
"""

import asyncio
from asyncio import Semaphore
import json
import hashlib
from typing import Dict
from datetime import datetime
from openai import AsyncOpenAI, RateLimitError, APIStatusError


class CompetencyAgent:
    """역량 평가 Agent"""
    
    # 필수 필드 정의
    REQUIRED_FIELDS = {
        "competency_name": str,
        "overall_score": int,
        "strengths": list,
        "weaknesses": list,
        "key_observations": list, 
        "perspectives": dict,
        "confidence": dict
    }
    
    def __init__(
        self,
        openai_client: AsyncOpenAI,
        max_concurrent: int = 5,
        max_retries: int = 5,
    ):
        self.client = openai_client
        self.model = "gpt-4o"
        self.semaphore = Semaphore(max_concurrent)
        self.cache = {}
        self.max_retries = max_retries
    
    def _get_cache_key(self, competency_name: str, transcript: Dict) -> str:
        """캐시 키 생성"""
        transcript_str = json.dumps(transcript, sort_keys=True, ensure_ascii=False)
        transcript_hash = hashlib.md5(transcript_str.encode()).hexdigest()
        return f"{competency_name}:{transcript_hash}"
    
    
    def _validate_and_fix_response(
        self, 
        result: Dict, 
        competency_name: str
    ) -> Dict:
        """
        LLM 응답 검증 및 필수 필드 보강
        
        Args:
            result: LLM이 반환한 JSON
            competency_name: 역량 이름
        
        Returns:
            검증 및 보강된 JSON
        """
        
        print(f"  [검증] {competency_name} 응답 검증 중...")
        
        # 1. 필수 필드 존재 여부 확인
        missing_fields = []
        for field, field_type in self.REQUIRED_FIELDS.items():
            if field not in result:
                missing_fields.append(field)
                print(f"    ⚠️  필수 필드 누락: {field}")
        
        
        # 2. key_observations 누락 시 자동 생성
        if "key_observations" not in result or not result.get("key_observations"):
            print(f"    🔧 key_observations 자동 생성 중...")
            
            # strengths, weaknesses, perspectives에서 핵심 관찰 추출
            key_obs = self._generate_key_observations(result, competency_name)
            result["key_observations"] = key_obs
            
            print(f"    ✅ key_observations 생성 완료 ({len(key_obs)}개)")
        else:
            print(f"    ✅ key_observations 존재 ({len(result['key_observations'])}개)")
        
        
        # 3. 빈 리스트 필드 경고
        if not result.get("strengths"):
            print(f"    ⚠️  strengths 비어있음")
        
        if not result.get("weaknesses"):
            print(f"    ⚠️  weaknesses 비어있음")
        
        
        # 4. 점수 범위 검증
        score = result.get("overall_score", 0)
        if not (0 <= score <= 100):
            print(f"    ⚠️  overall_score 범위 오류: {score} → 50으로 조정")
            result["overall_score"] = 50
        
        
        return result
    
    
    def _generate_key_observations(
        self, 
        result: Dict, 
        competency_name: str
    ) -> list:
        """
        key_observations 자동 생성
        
        전략:
            1. strengths/weaknesses에서 상위 3개 추출
            2. perspectives.evidence_reasoning에서 핵심 문장 추출
            3. 최소 3개 보장
        """
        
        key_obs = []
        
        # 1. Strengths에서 추출 (상위 2개)
        strengths = result.get("strengths", [])
        if strengths:
            key_obs.extend(strengths[:2])
        
        
        # 2. Weaknesses에서 추출 (상위 1개)
        weaknesses = result.get("weaknesses", [])
        if weaknesses:
            key_obs.append(weaknesses[0])
        
        
        # 3. Evidence reasoning에서 핵심 문장 추출
        perspectives = result.get("perspectives", {})
        evidence_reasoning = perspectives.get("evidence_reasoning", "")
        
        if evidence_reasoning:
            # "따라서", "전반적으로" 같은 키워드 뒤 문장 추출
            import re
            # "따라서 X점 산정" 같은 결론 문장 찾기
            conclusion_match = re.search(r'(따라서|전반적으로|종합하면)[^.]+\.', evidence_reasoning)
            if conclusion_match:
                conclusion = conclusion_match.group(0).strip()
                if conclusion not in key_obs:
                    key_obs.append(conclusion)
        
        
        # 4. 최소 3개 보장 (부족하면 기본 메시지 추가)
        if len(key_obs) < 3:
            score = result.get("overall_score", 0)
            
            # 점수 대역별 기본 관찰
            if score >= 75:
                key_obs.append(f"{competency_name} 역량이 신입 기준 우수한 수준")
            elif score >= 60:
                key_obs.append(f"{competency_name} 역량이 신입 기준 양호한 수준")
            elif score >= 50:
                key_obs.append(f"{competency_name} 역량이 신입 기준 평균 수준")
            else:
                key_obs.append(f"{competency_name} 역량이 신입 기준 미흡한 수준")
        
        
        # 5. 중복 제거 및 최대 5개로 제한
        key_obs = list(dict.fromkeys(key_obs))[:5]
        
        return key_obs
    
    
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
                for attempt in range(self.max_retries):
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
                        
                        # 🆕 필수 필드 검증 및 보강
                        result = self._validate_and_fix_response(result, competency_name)
                        
                        # 메타 정보 추가
                        result["competency_name"] = competency_name
                        result["competency_display_name"] = competency_display_name
                        result["competency_category"] = competency_category
                        result["evaluated_at"] = datetime.now().isoformat()
                        
                        # 캐싱
                        self.cache[cache_key] = result
                        
                        print(f"[평가 완료] {competency_name}: {result.get('overall_score', 0)}점")
                        
                        return result
                        
                    except RateLimitError as e:
                        await self._handle_rate_limit(e, attempt, competency_name)
                        continue
                    except APIStatusError as e:
                        if e.status_code == 429:
                            await self._handle_rate_limit(e, attempt, competency_name)
                            continue
                        raise
                    except json.JSONDecodeError as e:
                        if attempt < self.max_retries - 1:
                            print(f"[재시도 {attempt+1}/{self.max_retries}] {competency_name}: JSON 파싱 오류 → 백오프 후 재시도")
                            await asyncio.sleep(1 + attempt)
                        else:
                            raise
                    except Exception as e:
                        if attempt < self.max_retries - 1:
                            print(f"[재시도 {attempt+1}/{self.max_retries}] {competency_name}: {e}")
                            await asyncio.sleep(1 + attempt)
                        else:
                            raise
                            
            except Exception as e:
                raise RuntimeError(f"[{competency_name}] 평가 실패: {e}")

    async def _handle_rate_limit(self, error: Exception, attempt: int, competency_name: str):
        """429 오류 대응: retry-after 또는 지수 백오프 기반 대기"""
        retry_after = None
        response = getattr(error, "response", None)
        if response:
            retry_after = response.headers.get("retry-after") or response.headers.get("Retry-After")
        if retry_after:
            try:
                wait_seconds = float(retry_after)
            except ValueError:
                wait_seconds = None
        else:
            wait_seconds = None
        if wait_seconds is None:
            import re
            match = re.search(r"try again in ([0-9.]+)s", str(error))
            if match:
                wait_seconds = float(match.group(1))
        if wait_seconds is None:
            wait_seconds = min(30, 2 ** attempt * 2)
        print(f"[대기] {competency_name} rate limit 감지 → {wait_seconds:.1f}s 후 재시도 ({attempt+1}/{self.max_retries})")
        await asyncio.sleep(wait_seconds)


async def evaluate_all_competencies(
    agent: CompetencyAgent,
    transcript: Dict,
    prompts: Dict[str, str]
) -> Dict[str, Dict]:
    """10개 역량 배치 평가"""
    
    print("=" * 60)
    print("10개 역량 배치 평가 시작")
    print("=" * 60)
    
    # 10개 역량 설정
    competency_configs = [
        # Common Competencies (5개)
        ("achievement_motivation", "성취/동기 역량", "common"),
        ("growth_potential", "성장 잠재력", "common"),
        ("interpersonal_skill", "대인관계 역량", "common"), 
        ("organizational_fit", "조직 적합성", "common"),
        ("problem_solving", "문제해결력", "common"),
        
        # Job Competencies (5개)
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
                },
                "key_observations": [f"{name} 평가 실패"]  # 🆕 에러 시에도 필드 보장
            }
        else:
            result_dict[name] = result
    
    return result_dict
