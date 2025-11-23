"""
Presentation Formatter Node
프론트엔드용 데이터 재구성 + LLM 배치 근거 재생성
"""

import json
from typing import Dict, List
from datetime import datetime
from openai import AsyncOpenAI
from pathlib import Path


class PresentationFormatter:
    """
    프론트엔드용 데이터 변환기
    
    핵심 기능:
        1. LLM 배치 호출로 모든 역량 근거 한 번에 재생성
        2. Strengths/Weaknesses/Key_observations 평서형 변환
        3. Resume 검증 결과 포함
        4. 역량별 근거 그룹핑 (segment 여러 개)
        5. Transcript 매핑 정보 포함
        6. 직무/공통 점수 계산
    """
    
    # 역량명 한글 매핑
    COMPETENCY_DISPLAY_NAMES = {
        "achievement_motivation": "성취/동기 역량",
        "growth_potential": "성장 잠재력",
        "interpersonal_skill": "대인관계 역량",
        "organizational_fit": "조직 적합성",
        "problem_solving": "문제 해결",
        "customer_journey_marketing": "고객 여정 마케팅",
        "md_data_analysis": "MD 데이터 분석",
        "seasonal_strategy_kpi": "시즌 전략 KPI",
        "stakeholder_collaboration": "이해관계자 협업",
        "value_chain_optimization": "가치사슬 최적화",
    }
    
    # 역량 그룹 정의
    JOB_COMPETENCIES = [
        "customer_journey_marketing",
        "md_data_analysis", 
        "seasonal_strategy_kpi",
        "stakeholder_collaboration",
        "value_chain_optimization"
    ]
    
    COMMON_COMPETENCIES = [
        "achievement_motivation",
        "growth_potential",
        "interpersonal_skill",
        "organizational_fit",
        "problem_solving"
    ]
    
    
    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client
        self._transcript_data = None
    
    
    async def format(
        self,
        final_result: Dict,
        aggregated_competencies: Dict,
        competency_weights: Dict[str, float],
        transcript: Dict 
    ) -> Dict:
        """
        프론트엔드용 응답 생성
        
        Returns:
            {
                "overall_summary": {...},
                "score_breakdown": {...},
                "competency_scores": [...],
                "competency_details": {...}  
            }
        """
        
        print("\n[Presentation Formatter] 근거 배치 재생성 시작...")
        
        # 1. 전체 요약
        overall_summary = self._extract_overall_summary(final_result)
        
        # 2. 점수 분해 (전체/직무/공통)
        score_breakdown = self._calculate_score_breakdown(
            aggregated_competencies,
            competency_weights,
            final_result
        )
        
        # 3. 역량별 점수
        competency_scores = final_result.get("competency_scores", [])
        
        # 4. 배치로 모든 역량 재생성 (LLM 1회 호출)
        #    - Evidences
        #    - Strengths (평서형)
        #    - Weaknesses (평서형)
        #    - Key_observations (평서형)
        print(f"  10개 역량의 근거/강점/약점/관찰을 1번의 LLM 호출로 배치 생성 중...")
        
        batch_result = await self._regenerate_all_batch(
            aggregated_competencies,
            transcript
        )
        
        # 5. 역량별 상세 구성
        competency_details = {}
        
        for comp_name, comp_data in aggregated_competencies.items():
            comp_batch = batch_result.get(comp_name, {})
            
            competency_details[comp_name] = {
                "competency_display_name": self.COMPETENCY_DISPLAY_NAMES.get(comp_name, comp_name),
                "overall_score": comp_data.get("overall_score"),
                "confidence_v2": comp_data.get("confidence_v2"),
                
                # 평서형으로 재생성
                "strengths": comp_batch.get("strengths", comp_data.get("strengths", [])),
                "weaknesses": comp_batch.get("weaknesses", comp_data.get("weaknesses", [])),
                "key_observations": comp_batch.get("key_observations", comp_data.get("key_observations", [])),
                
                # 재생성된 근거
                "evidences": comp_batch.get("evidences", []),
                
                # Resume 검증 결과
                "resume_verification_summary": comp_data.get("resume_verification_summary", {
                    "verified_count": 0,
                    "high_strength_count": 0,
                    "key_evidence": []
                })
            }
        
        total_evidences = sum(len(cd.get('evidences', [])) for cd in competency_details.values())
        print(f"  배치 생성 완료: 총 {total_evidences}개 근거")
        
        return {
            "overall_summary": overall_summary,
            "score_breakdown": score_breakdown,
            "competency_scores": competency_scores,
            "competency_details": competency_details
        }
    
    
    def _extract_overall_summary(self, final_result: Dict) -> Dict:
        """전체 요약 추출"""
        return {
            "final_score": final_result.get("final_score"),
            "avg_confidence": final_result.get("avg_confidence"),
            "reliability": final_result.get("reliability"),
            "overall_evaluation_summary": final_result.get("overall_evaluation_summary")
        }
    
    
    def _calculate_score_breakdown(
        self,
        aggregated_competencies: Dict,
        competency_weights: Dict[str, float],
        final_result: Dict
    ) -> Dict:
        """
        점수 분해 계산 (전체/직무/공통)
        """
        
        # 직무 역량 점수
        job_total = 0.0
        job_weight_sum = 0.0
        
        for comp_name in self.JOB_COMPETENCIES:
            if comp_name in aggregated_competencies:
                score = aggregated_competencies[comp_name].get("overall_score", 0)
                weight = competency_weights.get(comp_name, 0)
                job_total += score * weight
                job_weight_sum += weight
        
        job_score = round(job_total / job_weight_sum, 1) if job_weight_sum > 0 else 0.0
        
        # 공통 역량 점수
        common_total = 0.0
        common_weight_sum = 0.0
        
        for comp_name in self.COMMON_COMPETENCIES:
            if comp_name in aggregated_competencies:
                score = aggregated_competencies[comp_name].get("overall_score", 0)
                weight = competency_weights.get(comp_name, 0)
                common_total += score * weight
                common_weight_sum += weight
        
        common_score = round(common_total / common_weight_sum, 1) if common_weight_sum > 0 else 0.0
        
        return {
            "final_score": final_result.get("final_score"),
            "job_score": job_score,
            "common_score": common_score,
            "job_competencies": self.JOB_COMPETENCIES,
            "common_competencies": self.COMMON_COMPETENCIES
        }
    
    
    async def _regenerate_all_batch(
        self,
        aggregated_competencies: Dict,
        transcript: Dict
    ) -> Dict[str, Dict]:

        self.transcript = transcript
    
        """
        배치: 모든 역량의 근거/강점/약점/관찰을 1번의 LLM 호출로 재생성
        
        Returns:
            {
                "achievement_motivation": {
                    "evidences": [...],
                    "strengths": ["평서형 강점1", "평서형 강점2", ...],
                    "weaknesses": ["평서형 약점1", ...],
                    "key_observations": ["평서형 관찰1", ...]
                },
                ...
            }
        """
        
        # 1. 모든 역량 데이터 수집
        all_competencies_data = []
        
        for comp_name, comp_data in aggregated_competencies.items():
            perspectives = comp_data.get("perspectives", {})
            evidence_details = perspectives.get("evidence_details", [])

            for ev in evidence_details:
                segment_id = ev.get("segment_id")
                char_index = ev.get("char_index")
                
                # char_length 확인 및 계산
                if "char_length" not in ev or ev["char_length"] is None:
                    ev["char_length"] = len(ev.get("text", ""))
                
                # Transcript에서 실제 텍스트 추가
                if segment_id and char_index is not None:
                    actual_text = self._get_transcript_text(segment_id, char_index)
                    ev["actual_transcript_text"] = actual_text

            all_competencies_data.append({
                "competency_name": comp_name,
                "competency_display_name": self.COMPETENCY_DISPLAY_NAMES.get(comp_name, comp_name),
                "overall_score": comp_data.get("overall_score", 0),
                
                # Evidence 데이터
                "evidence_details": perspectives.get("evidence_details", []),
                "evidence_reasoning": perspectives.get("evidence_reasoning", ""),
                
                # Behavioral 데이터
                "behavioral_pattern": perspectives.get("behavioral_pattern", {}),
                "behavioral_reasoning": perspectives.get("behavioral_reasoning", ""),
                
                # Critical 데이터
                "red_flags": perspectives.get("red_flags", []),
                "critical_reasoning": perspectives.get("critical_reasoning", ""),
                
                # 원본 Strengths/Weaknesses/Key_observations
                "original_strengths": comp_data.get("strengths", []),
                "original_weaknesses": comp_data.get("weaknesses", []),
                "original_key_observations": comp_data.get("key_observations", [])
            })
        
        # 1.5. transcript에서 실제 텍스트 추가
        for comp_data in all_competencies_data:
            evidence_details = comp_data["evidence_details"]
            
            for ev in evidence_details:
                segment_id = ev.get("segment_id")
                char_index = ev.get("char_index")
                
                # transcript에서 실제 텍스트 가져오기
                if segment_id and char_index is not None:
                    actual_text = self._get_transcript_text(segment_id, char_index)
                    ev["actual_transcript_text"] = actual_text
        
        # 2. 배치 프롬프트 생성
        prompt = self._build_comprehensive_batch_prompt(all_competencies_data)
        
        # 3. LLM 1회 호출
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at synthesizing competency evaluation data into clear, professional summaries for HR reports."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=12000,  # 근거+강점+약점+관찰 모두 포함이므로 토큰 더 많이 필요
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content.strip()
            result = json.loads(result_text)
            
            # 4. 역량별로 파싱
            batch_by_competency = {}
            
            for comp_result in result.get("competencies", []):
                comp_name = comp_result.get("competency_name")
                batch_by_competency[comp_name] = {
                    "evidences": comp_result.get("evidences", []),
                    "strengths": comp_result.get("strengths", []),
                    "weaknesses": comp_result.get("weaknesses", []),
                    "key_observations": comp_result.get("key_observations", [])
                }
            
            return batch_by_competency
        
        except Exception as e:
            print(f"        배치 LLM 호출 실패: {e}")
            import traceback
            traceback.print_exc()
            # Fallback: 원본 데이터 그대로 반환
            return self._fallback_all_batch(aggregated_competencies)
    
    
    def _build_comprehensive_batch_prompt(
        self,
        all_competencies_data: List[Dict]
    ) -> str:
        """
        종합 배치 재생성 프롬프트 (근거 + 강점 + 약점 + 관찰)
        """
        
        template = """# Task: 10개 역량 평가 데이터 종합 배치 재생성

당신은 HR 평가 보고서 작성 전문가입니다.
10개 역량에 대한 **근거, 강점, 약점, 핵심 관찰**을 **한 번에** 평서문으로 재작성해야 합니다.

## 입력 데이터:
```json
__COMPETENCY_DATA__
```
## 🔥 CRITICAL: 원본 Segment 정보 절대 보존 규칙

**절대 규칙:**
- ✅ **최소 2개** (예외 없음)
- ✅ **최대 8개**
- ❌ **빈 배열 [] 절대 금지**
- ❌ **1개만 있는 것도 금지**

**모든 evidences는 반드시 원본 데이터의 segment_id, char_index, char_length를 그대로 사용해야 합니다.**

### ✅ 올바른 방법:
```json
// 원본 evidence_details:
{
  "segment_id": 3,
  "char_index": 1200,
  "char_length": 45,
  "text": "..."
}

// 출력 evidences (원본 값 그대로):
{
  "summary": "지원자는 ...",
  "segment_id": 3,        // ✅ 원본 유지
  "char_index": 1200,     // ✅ 원본 유지
  "char_length": 45,      // ✅ 원본 유지
  "impact": "positive"
}
```

### ❌ 절대 금지:
- segment_id, char_index, char_length를 임의로 생성 ❌
- 원본 값을 0으로 변경 ❌
- 고정값(50, 60, 80) 반복 사용 ❌

### 📌 Evidences 생성 규칙:

1. **evidence_details가 있는 경우:**
   - 각 evidence_detail을 1개의 positive evidence로 변환
   - segment_id, char_index, char_length는 **원본 값 그대로 사용**
   - summary만 2-3문장으로 재작성

2. **red_flags가 있는 경우:**
   - 각 red_flag를 1개의 negative evidence로 변환
   - evidence_reference에서 segment_id, char_index 파싱
   - char_length는 description 길이 기준으로 추정

3. **둘 다 없는 경우:**
   - behavioral_pattern.specific_examples에서 segment 번호 찾기
   - 그래도 없으면 evidences: [] (빈 배열)
```

---

### 📌 Segment 정보 추출 우선순위:

**1순위: evidence_details**
```json
{
  "segment_id": 3,
  "char_index": 1200
}
```

**2순위: behavioral_pattern.specific_examples**
```
"모든 주요 경험(3개)에서 자발적 시작 (Segment 3, 7, 11)"
→ segment_id: 3, 7, 11 추출
```

**3순위: behavioral_reasoning**
```
"Segment 9에서 끈기 명확..."
→ segment_id: 9 추출
```

**4순위: red_flags.evidence_reference**
```
"segment_id: 9, char_index: 3450-3500"
→ segment_id: 9, char_index: 3450 추출
```

**5순위: critical_reasoning**
```
"Segment 5에서 외적 동기..."
→ segment_id: 5 추출
```

**모든 방법으로도 segment를 찾을 수 없으면:**
→ 해당 역량의 evidences는 `[]` 빈 배열

---

**검증 규칙:**
- ✅ 모든 evidence 항목의 segment_id는 1 이상이어야 함
- ✅ char_index는 0 이상이어야 함
- ✅ segment_id가 없으면 해당 evidence 항목 자체를 제외
- ❌ segment_id: 0, null, undefined 절대 금지
---
## Rule 4: char_index와 char_length 규칙

### char_index:
- **1순위 evidence_details에서 가져온 경우: 원본 값 그대로**
- **2순위 red_flags에서 파싱한 경우: 파싱된 값 사용**
- **3~5순위로 생성한 경우: 0 사용 (어쩔 수 없음)**

### char_length (하이라이트 범위):

**char_length의 의미:**
- 프론트엔드에서 transcript의 실제 텍스트를 하이라이트할 때 사용
- char_index부터 char_length만큼의 텍스트가 노란색으로 표시됨
- **반드시 실제로 의미 있는 단어/문장 범위여야 함**

**규칙:**

1. **1순위: evidence_details에서 가져온 경우**
```json
   {
     "char_index": 1200,
     "char_length": 45  // ✅ 원본 값 그대로 사용
   }
```

2. **2순위: red_flags에서 파싱한 경우**
```
   evidence_reference: "segment_id: 9, char_index: 3450-3500"
```
   → char_index: 3450, char_length: 50 (3500 - 3450)

3. **3~5순위: behavioral/critical에서 생성한 경우**
   - **원칙: transcript에서 실제로 하이라이트할 핵심 문장 길이를 추정**
   - **방법:**
     - 짧은 핵심 표현 (1~2단어): 10~30자
     - 한 문장: 30~80자
     - 두 문장: 80~150자
   - **예시:**
```json
     {
       "summary": "지원자는 '혼자 하는 게 더 편하다'고 언급했습니다.",
       "segment_id": 8,
       "char_index": 0,
       "char_length": 40  // "혼자 하는 게 더 편하다" 부분만 하이라이트
     }
```

### ✅ 좋은 예시:
```json
// evidence_details에서 가져온 경우
{
  "summary": "지원자는 교수님께 직접 연구 프로젝트를 제안하여 시작했습니다.",
  "segment_id": 3,
  "char_index": 1200,
  "char_length": 45,  // ✅ 원본 값 (실제 하이라이트 범위)
  "impact": "positive"
}

// red_flags에서 파싱한 경우
{
  "summary": "지원자는 '어려운 건 피하고 쉬운 걸로 선택했다'고 언급했습니다.",
  "segment_id": 9,
  "char_index": 3450,
  "char_length": 50,  // ✅ 3500 - 3450 = 50 (파싱된 범위)
  "impact": "negative"
}

// behavioral에서 생성한 경우
{
  "summary": "지원자는 협업보다 개인 작업을 선호한다고 언급했습니다.",
  "segment_id": 8,
  "char_index": 0,
  "char_length": 35,  // ✅ 핵심 문장 길이 추정 ("협업보다 개인 작업을 선호한다")
  "impact": "neutral"
}
```

### ❌ 나쁜 예시:
```json
// 모든 evidence에서 고정값 사용
{
  "char_length": 60  // ❌ 모든 evidence에서 60 반복
}

// 터무니없이 짧거나 긴 값
{
  "char_length": 5   // ❌ 너무 짧음 (하이라이트 안 보임)
}

{
  "char_length": 500  // ❌ 너무 김 (전체 답변 하이라이트)
}
```

### 🎯 char_length 결정 가이드:

**원칙: "이 evidence의 핵심이 되는 부분이 transcript에서 몇 글자 정도일까?"**

1. **핵심 키워드/표현만 하이라이트하고 싶으면:**
   - 예: "혼자 하는 게 더 편하다" → 20~40자
   
2. **한 문장을 하이라이트하고 싶으면:**
   - 예: "교수님께 직접 제안했어요." → 30~80자
   
3. **두 문장을 하이라이트하고 싶으면:**
   - 예: "제가 먼저 제안했어요. 궁금해서 물어봤거든요." → 80~150자

**⚠️ 주의:**
- char_index가 0인 경우 (정확한 위치 모름): 핵심 문장 길이를 보수적으로 추정 (40~80자)
- 같은 역량 내에서도 evidence마다 다른 값 사용 (고정값 반복 금지)

```
## 출력 요구사항:

### 1. Evidences (근거) 재생성
- Evidence, Behavioral, Critical을 **통합하여** 평서문으로 재작성
- 각 근거는 **2-3문장** (구어체 ❌, "~했습니다" ✅)
- 원본 텍스트를 재해석하여 의미 있게 서술

### 2. Strengths (강점) 평서형 변환
- 원본: "주도성 중상 (교수님께 먼저 제안, 자발적 시작)"
- 변환: "자발적이고 주도성이 높습니다."
- **각 강점을 1-2문장의 평서문으로**

### 3. Weaknesses (약점) 평서형 변환
- 원본: "자발성 부족 (모든 경험에서 수동적)"
- 변환: "대부분 상황에서 수동적입니다."
- **각 약점을 1-2문장의 평서문으로**

### 4. Key_observations (핵심 관찰) 평서형 변환
- 원본: "신입 치고는 자발성과 내적 동기가 명확 (상위 30% 추정)"
- 변환: "신입 기준 상위 30% 수준의 자발성을 보입니다."
- **각 관찰을 1-2문장의 평서문으로**
- **최소 3개 이상** (예외 없음)

### 5. 각 Evidence 항목 정보:
- **summary**: 평서문 형태의 근거 설명 (2-3문장)
- **segment_id**: transcript 위치
- **char_index**: transcript 시작 위치
- **char_length**: 하이라이트할 텍스트 길이 (20~80자)
- **impact**: "positive" / "negative" / "neutral"
- **evidence_type**: 근거 유형 (예: "주도성", "끈기")

### 6. 근거 개수 (역량별):
- Evidence details 개수만큼 positive 근거
- Red flags 개수만큼 negative 근거
- **최소 3개, 최대 8개**

---

## 평서문 작성 가이드:

✅ **좋은 예시 (근거) - 2-3문장:**
"지원자는 교수님께 직접 연구 프로젝트를 제안하여 시작했습니다. 이는 높은 주도성과 내적 동기를 보여주는 사례로, 스스로 '궁금해서' 먼저 물어보고 행동에 옮긴 점이 인상적입니다."

✅ **좋은 예시 (강점) - 1문장, 간결:**
"자발적이고 주도성이 높습니다."
"도전적인 목표를 설정하고 끝까지 완수합니다."
"실패 후에도 재도전하는 끈기가 있습니다."

✅ **좋은 예시 (약점) - 1문장, 간결:**
"일부 상황에서 도전을 회피합니다."
"프로젝트 완수율이 다소 낮습니다."
"외적 동기에 의존하는 경향이 있습니다."

✅ **좋은 예시 (관찰) - 1문장, 간결:**
"신입 기준 상위 30% 수준의 자발성을 보입니다."
"모든 프로젝트에서 일관된 주도성을 보입니다."
"입사 후 어려운 과제에도 포기하지 않을 것으로 기대됩니다."

❌ **나쁜 예시 (강점/약점/관찰) - 너무 길고 장황함:**
"지원자는 교수님께 먼저 제안하며 연구 프로젝트를 자발적으로 시작하는 등 높은 주도성을 보여주었습니다." (X)
"동아리 활동 선택 시 어려운 과제를 회피하고 쉬운 옵션을 선택하는 경향이 일부 관찰되었습니다." (X)
"신입 지원자로서는 드물게 모든 프로젝트에서 일관된 자발적 시작 패턴을 보였으며, 이는 동일 직급 대비 상위 30% 수준의 주도성으로 평가됩니다." (X)


---

## 출력 형식 (JSON):
{{
  "competencies": [
    {{
      "competency_name": "achievement_motivation",
      
      "evidences": [
        {{
          "summary": "지원자는 교수님께 직접 연구 프로젝트를 제안하여 시작했습니다. 이는 높은 주도성과 내적 동기를 보여주는 사례로, 스스로 '궁금해서' 먼저 물어보고 행동에 옮긴 점이 인상적입니다.",
          "segment_id": 3,
          "char_index": 1200,
          "char_length": 45,
          "impact": "positive",
          "evidence_type": "주도성, 내적 동기"
        }},
        {{
          "summary": "지원자는 동아리 활동 선택 시 '어려운 건 피하고 쉬운 걸로 선택했다'고 언급했습니다. 이는 일부 상황에서 도전을 회피하는 경향을 시사합니다.",
          "segment_id": 9,
          "char_index": 3450,
          "char_length": 30,
          "impact": "negative",
          "evidence_type": "도전 회피"
        }}
      ],
      
      "strengths": [
        "자발적이고 주도성이 높습니다.",
        "도전적인 목표를 설정하고 끝까지 완수합니다.",
        "내적 동기가 명확합니다.",
        "실패 후에도 재도전하는 끈기가 있습니다."
      ],
      
      "weaknesses": [
        "일부 상황에서 도전을 회피합니다.",
        "프로젝트 완수율이 다소 낮습니다."
      ],
      
      "key_observations": [
        "신입 기준 상위 30% 수준의 자발성을 보입니다.",
        "모든 프로젝트에서 일관된 주도성을 보입니다.",
        "입사 후 어려운 과제에도 포기하지 않을 것으로 기대됩니다."
      ]
    }},
    {{
      "competency_name": "growth_potential",
      "evidences": [...],
      "strengths": [...],
      "weaknesses": [...],
      "key_observations": [...]
    }},
    ... (총 10개 역량)
  ]
}}

---

**중요:**
- 반드시 JSON만 출력 (마크다운 블록 ❌)
- 10개 역량 모두 포함
- **Evidences는 2-3문장 (상세)**
- **Strengths/Weaknesses/Key_observations는 1문장 (간결)**
- 원본 텍스트를 그대로 복사하지 말고, **의미를 재해석**
- Strengths는 최소 3개, 최대 6개
- Weaknesses는 최소 2개, 최대 4개
- Key_observations는 최소 3개, 최대 5개
"""
        
        prompt = template.replace(
            "__COMPETENCY_DATA__",
            json.dumps(all_competencies_data, ensure_ascii=False, indent=2)
        )

        return prompt

    def _get_transcript_text(self, segment_id: int, char_index: int) -> str:
        """
        테스트용 transcript에서 segment 답변 텍스트 일부를 반환.
        - 경로 우선순위: tests_data/ → server/test_data/ → test_data/
        - char_index가 주어지면 해당 위치에서 120자 슬라이스, 없으면 전체 답변 반환.
        """
        
        segments = self._transcript_data.get("segments", []) if isinstance(self._transcript_data, dict) else []
        segment = next((s for s in segments if s.get("segment_id") == segment_id), None)
        if not segment:
            return ""
        
        answer_text = segment.get("answer_text", "")
        if not isinstance(answer_text, str):
            return ""
        
        if isinstance(char_index, int) and 0 <= char_index < len(answer_text):
            return answer_text[char_index: char_index + 120]
        
        return answer_text
    
    
    def _fallback_all_batch(
        self,
        aggregated_competencies: Dict
    ) -> Dict[str, Dict]:
        """
        배치 LLM 실패 시 Fallback (원본 데이터 그대로)
        """
        
        fallback = {}
        
        for comp_name, comp_data in aggregated_competencies.items():
            perspectives = comp_data.get("perspectives", {})
            evidence_details = perspectives.get("evidence_details", [])
            red_flags = perspectives.get("red_flags", [])
            comp_evidences = []
            
            # Evidence details
            for ev in evidence_details:
                comp_evidences.append({
                    "summary": f"지원자는 다음과 같은 행동을 보였습니다: {ev.get('text', '')}",
                    "segment_id": ev.get("segment_id"),
                    "char_index": ev.get("char_index"),
                    "char_length": 50,
                    "impact": "positive",
                    "evidence_type": ev.get("relevance_note", "")
                })
            
            # Red flags
            for flag in red_flags:
                seg_id = self._extract_segment_id(flag.get("evidence_reference", ""))
                char_idx = self._extract_char_index(flag.get("evidence_reference", ""))
                
                comp_evidences.append({
                    "summary": flag.get("description", ""),
                    "segment_id": seg_id,
                    "char_index": char_idx,
                    "char_length": 30,
                    "impact": "negative",
                    "evidence_type": flag.get("flag_type", "")
                })
            
            fallback[comp_name] = {
                "evidences": comp_evidences,
                "strengths": comp_data.get("strengths", []),
                "weaknesses": comp_data.get("weaknesses", []),
                "key_observations": comp_data.get("key_observations", [])
            }
        
        return fallback
    
    
    @staticmethod
    def _extract_segment_id(evidence_reference: str) -> int:
        """evidence_reference에서 segment_id 추출"""
        try:
            if "segment_id:" in evidence_reference:
                segment_part = evidence_reference.split("segment_id:")[1].split(",")[0].strip()
                return int(segment_part)
        except:
            pass
        return None
    
    
    @staticmethod
    def _extract_char_index(evidence_reference: str) -> int:
        """evidence_reference에서 char_index 추출"""
        try:
            if "char_index:" in evidence_reference:
                char_part = evidence_reference.split("char_index:")[1].split("-")[0].strip()
                return int(char_part)
        except:
            pass
        return None


async def presentation_formatter_node(state) -> Dict:
    """
    Presentation Formatter Node
    
    프론트엔드용 데이터 재구성 + 배치 LLM 근거 재생성
    """
    
    start_time = datetime.now()
    
    print("\n" + "="*60)
    print("[Presentation Formatter] 프론트용 데이터 변환 시작")
    print("="*60)
    
    openai_client = state.get("openai_client")
    final_result = state.get("final_result", {})
    aggregated_competencies = state.get("aggregated_competencies", {})
    competency_weights = state.get("competency_weights", {})
    transcript = state.get("transcript")
    formatter = PresentationFormatter(openai_client)
    
    presentation_result = await formatter.format(
        final_result,
        aggregated_competencies,
        competency_weights,
        transcript
    )
    
    duration = (datetime.now() - start_time).total_seconds()
    
    total_evidences = sum(
        len(cd.get('evidences', [])) 
        for cd in presentation_result['competency_details'].values()
    )
    
    print(f"\n  총 근거 생성: {total_evidences}개")
    print(f"  강점/약점/관찰 평서형 변환: 10개 역량")
    print(f"  Resume 검증 결과 포함: 완료")
    print(f"  처리 시간: {duration:.2f}초")
    print(f"  배치 효율: 10개 역량 → 1회 LLM 호출")
    
    print("\n" + "="*60)
    print("[Presentation Formatter] 완료")
    print("="*60)
    
    return {
        "presentation_result": presentation_result,
        "execution_logs": state.get("execution_logs", []) + [{
            "node": "presentation_formatter",
            "duration_seconds": round(duration, 2),
            "total_evidences_generated": total_evidences,
            "batch_llm_calls": 1,
            "components_regenerated": ["evidences", "strengths", "weaknesses", "key_observations"],
            "timestamp": datetime.now().isoformat()
        }]
    }
