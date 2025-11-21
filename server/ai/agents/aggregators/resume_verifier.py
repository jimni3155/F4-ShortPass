"""
Resume Verifier
10개 Agent의 모든 Segment 평가를 Resume와 비교 (AI 1회 Batch)
"""

import json
from typing import Dict, List, Any
from openai import AsyncOpenAI


class ResumeVerifier:
    """
    Resume 검증기
    
    역할:
        - 10개 Agent의 모든 Segment 평가를 Resume와 비교
        - AI 1회 호출로 Batch 처리
        - 각 Segment 평가에 Resume 검증 결과 추가:
            * resume_verified: bool
            * verification_strength: "high"/"medium"/"low"/"none"
            * resume_evidence: List[str]
    """
    
    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client
    
    
    async def verify_batch(
        self,
        all_competency_results: Dict[str, Dict],
        resume_data: Dict
    ) -> List[Dict]:
        """
        Batch Resume 검증
        
        Args:
            all_competency_results: 10개 역량 평가 결과
                {
                    "achievement_motivation": {...},
                    "growth_potential": {...},
                    ...
                }
            resume_data: 파싱된 Resume JSON
                {
                    "education": [...],
                    "experience": [...],
                    "projects": [...],
                    "skills": [...]
                }
        
        Returns:
            segment_evaluations_with_resume: Resume 검증 추가된 Segment 평가 목록
                [
                    {
                        "competency": "achievement_motivation",
                        "segment_id": 3,
                        "score": 85,
                        "quotes": [...],
                        "interview_confidence": 0.85,
                        "resume_verified": true,
                        "verification_strength": "high",
                        "resume_evidence": ["학부생 창업 경험", ...]
                    },
                    ...
                ]
        """
        
        # 1. Segment 평가 목록 추출
        segment_evaluations = self._extract_segment_evaluations(all_competency_results)
        
        print(f"\n[Resume Verifier] Segment 평가 추출: {len(segment_evaluations)}개")
        
        # Resume 데이터 없으면 검증 스킵
        if not resume_data:
            print("  Resume 데이터 없음 - 검증 스킵")
            return self._add_empty_verification(segment_evaluations)
        
        
        # 2. AI 프롬프트 생성
        prompt = self._build_verification_prompt(segment_evaluations, resume_data)
        
        
        # 3. AI 호출 (1회)
        print("[Resume Verifier] AI 호출 시작 (Batch)...")
        
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a resume verification expert. Verify if interview segment evaluations are supported by the candidate's resume."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        result_text = response.choices[0].message.content
        print(f"[Resume Verifier] AI 응답 길이: {len(result_text)} chars")
        
        
        # 4. 결과 파싱
        try:
            verification_results = json.loads(result_text)
            verified_list = verification_results.get("verifications", [])
            
            print(f"[Resume Verifier] 검증 완료: {len(verified_list)}개")
            
            # 원본 Segment 평가와 병합
            merged = self._merge_verification_results(
                segment_evaluations,
                verified_list
            )
            
            return merged
        
        except json.JSONDecodeError as e:
            print(f"  JSON 파싱 실패: {e}")
            return self._add_empty_verification(segment_evaluations)
    
    
    def _extract_segment_evaluations(
        self,
        all_competency_results: Dict[str, Dict]
    ) -> List[Dict]:
        """
        10개 역량 결과에서 Segment 평가 추출
        
        Returns:
            [
                {
                    "competency": "achievement_motivation",
                    "segment_id": 3,
                    "score": 85,
                    "quotes": [...],
                    "interview_confidence": 0.85
                },
                ...
            ]
        """
        segment_evals = []
        
        for comp_name, comp_result in all_competency_results.items():
            if not comp_result:
                continue
            
            # Evidence details에서 Segment 평가 추출
            perspectives = comp_result.get("perspectives", {})
            evidence_details = perspectives.get("evidence_details", [])
            overall_score = comp_result.get("overall_score", 0)
            overall_confidence = comp_result.get("confidence", {}).get("overall_confidence", 0.5)
            
            for detail in evidence_details:
                segment_eval = {
                    "competency": comp_name,
                    "segment_id": detail.get("segment_id"),
                    "quote_text": detail.get("text", ""),
                    "relevance_note": detail.get("relevance_note", ""),
                    "quality_score": detail.get("quality_score", 0.0),
                    "overall_score": overall_score,
                    "score": overall_score,
                    "interview_confidence": overall_confidence 
                }
                segment_evals.append(segment_eval)
        
        return segment_evals
    
    
    def _build_verification_prompt(
        self,
        segment_evaluations: List[Dict],
        resume_data: Dict
    ) -> str:
        """
        AI 검증 프롬프트 생성
        """
        prompt = f"""# Task: Resume Verification (Batch)

Verify if the following interview segment evaluations are supported by the candidate's resume.

## Resume Data:
```json
{json.dumps(resume_data, ensure_ascii=False, indent=2)}
```

## Segment Evaluations to Verify:
```json
{json.dumps(segment_evaluations, ensure_ascii=False, indent=2)}
```

## Instructions:
For each segment evaluation, check if the claims are supported by resume evidence.

Output JSON format:
{{
  "verifications": [
    {{
      "competency": "achievement_motivation",
      "segment_id": 3,
      "resume_verified": true,
      "verification_strength": "high",  // "high"/"medium"/"low"/"none"
      "resume_evidence": ["학부생 창업 경험", "프로젝트 수상 경력"]
    }},
    ...
  ]
}}

Verification Strength Guidelines:
- "high": Strong evidence in resume (직접적 경험)
- "medium": Indirect evidence (관련 경험)
- "low": Weak connection (추정 가능)
- "none": No evidence in resume

CRITICAL: Output ONLY valid JSON. NO markdown, NO explanations.
"""
        return prompt
    
    
    def _merge_verification_results(
        self,
        original_segments: List[Dict],
        verified_list: List[Dict]
    ) -> List[Dict]:
        """
        원본 Segment 평가 + Resume 검증 결과 병합
        """
        # Verification 결과를 dict로 변환 (빠른 조회)
        verification_map = {}
        for v in verified_list:
            key = (v.get("competency"), v.get("segment_id"))
            verification_map[key] = v
        
        # 병합
        merged = []
        for seg in original_segments:
            key = (seg.get("competency"), seg.get("segment_id"))
            verification = verification_map.get(key, {})
            
            merged_seg = {
                **seg,
                "resume_verified": verification.get("resume_verified", False),
                "verification_strength": verification.get("verification_strength", "none"),
                "resume_evidence": verification.get("resume_evidence", [])
            }
            merged.append(merged_seg)
        
        return merged
    
    
    def _add_empty_verification(
        self,
        segment_evaluations: List[Dict]
    ) -> List[Dict]:
        """
        Resume 검증 없이 빈 필드 추가
        """
        return [
            {
                **seg,
                "resume_verified": False,
                "verification_strength": "none",
                "resume_evidence": []
            }
            for seg in segment_evaluations
        ]
