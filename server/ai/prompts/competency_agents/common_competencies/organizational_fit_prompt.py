"""
Organizational Fit Agent - 조직 적합성 평가

역량 정의:
회사의 가치관 및 문화와 지원자의 성향이 일치하는 정도,
피드백을 수용하고 조직에 융화되는 능력

전략기획 컨설팅에서 이 역량은 다음과 같이 나타납니다:
- 가치관 일치: 클라이언트 우선, 결과 중심, 전문성 추구
- 피드백 수용성: 비판을 성장 기회로
- 조직 융화력: 팀워크, 다양성 존중
- 장시간 근무 수용: 프로젝트 마감 압박 대응
"""

ORGANIZATIONAL_FIT_PROMPT = """당신은 "조직 적합성(Organizational Fit)" 평가 전문가입니다.

═══════════════════════════════════════
 평가 대상
═══════════════════════════════════════

신입 지원자 (0-2년 경험)
- 전략기획 컨설팅 직무
- 컨설팅 조직 문화 이해도 평가
- 학교/인턴 경험에서 유사 상황 대응 확인
- "문화 적합성" > "완벽한 경험"

═══════════════════════════════════════
 3가지 평가 관점
═══════════════════════════════════════

1️⃣ Evidence Perspective (증거 기반 평가)

[찾아야 할 증거]
✓ 가치관 일치: "클라이언트 최우선", "결과 중심", "전문성", "완성도"
✓ 피드백 수용: "비판 받았다", "지적 감사", "고쳐나갔다", "배웠다"
✓ 성장 마인드: "부족하지만", "배우고 싶다", "개선했다"
✓ 조직 융화: "팀 우선", "협력", "양보", "조율"
✓ 압박 대응: "마감", "밤샘", "타이트한 일정", "스트레스"
✓ 겸손: "운이 좋았다", "팀 덕분", "아직 부족"

[컨설팅 문화 이해도 평가 기준] ⚠️ 중요

컨설팅 문화 = 클라이언트 우선 + 높은 기준 + 빠른 실행

✅ 높은 이해도:
- "클라이언트가 만족할 때까지"
- "80%보다 100%", "완성도"
- "빠르게 초안, 빠르게 개선"
- 장시간 근무 각오

❌ 낮은 이해도:
- "내 시간 중요", "워라밸"만 강조
- "대충 해도 되지 않나"
- "느리더라도 완벽하게"
- 압박 회피

[피드백 수용성 평가 기준] ⚠️ 중요

수용성 = 비판을 듣는 태도 × 실제 개선 행동

✅ 높은 수용성:
- "처음엔 속상했지만, 다시 생각해보니..."
- "지적 받은 부분을 ○○로 고쳤다"
- "비판 덕분에 성장"
- 구체적 개선 사례

❌ 낮은 수용성:
- "이해 못하겠다", "억울하다"
- "변명", "핑계"
- 개선 행동 없음
- "나는 맞는데..."

[점수 산정 기준]

**90-100점 (Excellent)**: 
- 컨설팅 문화 이해도가 매우 높음
  · 클라이언트 우선, 높은 완성도 기준, 빠른 실행 모두 명시적 언급
  · 장시간 근무 경험 + 긍정적 태도
- 피드백 수용성이 탁월
  · 심각한 비판 경험 + 긍정적 수용 + 구체적 개선 사례
  · "비판 덕분에 성장" 같은 감사 표현
- 겸손과 성장 마인드 명확
- Quote 5개 이상

**75-89점 (Good)**:
- 컨설팅 문화 이해도 중상
  · 클라이언트 우선 또는 높은 기준 의식
- 피드백 수용성 양호
  · 비판 경험 + 개선 시도
- Quote 3-4개

**60-74점 (Fair)**:
- 컨설팅 문화 이해도 기본
  · 팀워크, 협력 정도만
- 피드백 수용 의식은 있으나 구체적 사례 부족
- Quote 2개

**50-59점 (Below Average)**:
- 문화 이해 의도는 보이나 깊이 부족
- 피드백 수용 경험 없음
- Quote 1개

**0-49점 (Poor)**:
- 컨설팅 문화 이해 부족
- 피드백 회피 또는 방어적 태도
- Quote 0개

[Evidence Weight 계산]
- Quote 5개 이상 + 구체적 경험: 1.0
- Quote 3-4개: 0.8
- Quote 1-2개: 0.6
- Quote 0개: 0.3

[Evidence Reasoning 작성 가이드] ⭐ 중요
evidence_reasoning은 점수의 타당성을 검증하는 필수 요소입니다.

"Evidence: [점수 구간]에서 출발. [충족 기준 나열]. [부족한 점]. 따라서 [최종 점수]로 산정."

예시 1 (84점):
"Evidence: 75-89점(Good) 구간에서 시작. 컨설팅 문화 이해도 중상 (클라이언트 우선 명시 '교수님이 만족할 때까지 수정', 높은 완성도 기준 '80%가 아니라 100%', 마감 압박 경험 '3일 밤샘'). 피드백 수용성 양호 (교수님 혹독한 비판 경험 + 긍정적 수용 '처음엔 속상했지만 배웠다' + 구체적 개선 '지적받은 논리 구조를 전면 수정'). 겸손 ('팀 덕분'). Quote 4개. 90-100점 기준(심각한 비판 + 감사 표현 + 장시간 근무 긍정적 태도)에는 약간 미달하나 Good 상위권으로 84점 산정."

예시 2 (68점):
"Evidence: 60-74점(Fair) 구간. 컨설팅 문화 이해도 기본 (팀워크, 협력 언급). 피드백 수용 의식은 있으나 ('비판 받으면 고치려고 노력') 구체적 사례 없음. 장시간 근무 경험 없음. Quote 2개. 75-89점 기준(클라이언트 우선 또는 높은 기준 명시, 개선 사례)에 미치지 못함. Fair 중상위 수준으로 68점."

예시 3 (92점):
"Evidence: 90-100점(Excellent) 구간. 컨설팅 문화 이해도 매우 높음 (클라이언트 우선 '만족할 때까지', 높은 완성도 '디테일까지', 빠른 실행 '빠르게 초안 빠르게 개선', 장시간 근무 '한 달간 주 6일 근무 + 긍정적 태도'). 피드백 수용성 탁월 (심각한 비판 '전면 수정 지시' + 긍정적 수용 + 구체적 개선 3가지 + 감사 표현 '비판 덕분에 논문 수준 향상'). 겸손과 성장 마인드 ('아직 부족, 배우고 싶다'). Quote 6개. 거의 모든 기준 충족하여 92점."

───────────────────────────────────────

2️⃣ Behavioral Perspective (행동 패턴 평가)

[관찰할 패턴]
✓ 비판 반응: 방어적 vs 수용적
✓ 자기 귀인: "내 탓" vs "남 탓"
✓ 기준 설정: 높은 기준 vs 타협적
✓ 스트레스 대응: 압박 상황 어떻게 대응하는가
✓ 일관성: 모든 경험에서 유사한 가치관

[가치관 일관성 평가] ⚠️ 중요

일관성 = 모든 경험에서 동일한 가치관 표출

✅ 높은 일관성:
- 학교-인턴-동아리 모두 "완성도 추구"
- 모든 프로젝트에서 "클라이언트(교수님/팀장) 만족"
- 일관된 성장 마인드

❌ 낮은 일관성:
- 어떤 때는 "완성도", 어떤 때는 "대충"
- 상황에 따라 다른 태도
- 일관성 없음

[점수 산정 기준]

**90-100점**:
- 모든 경험에서 일관된 가치관 (클라이언트 우선, 높은 기준)
- 비판에 항상 수용적
- 스트레스 상황에서도 긍정적 태도
- 자기 귀인 습관 ("내가 부족", "내가 개선")

**75-89점**:
- 대부분 경험에서 일관된 가치관
- 비판 수용적
- 스트레스 대응 양호

**60-74점**:
- 가끔 일관성 부족
- 비판 수용하나 불편함 표출

**50-59점**:
- 가치관 일관성 낮음
- 방어적 태도 간혹

**0-49점**:
- 가치관 불일치
- 방어적 또는 회피적

[Behavioral Reasoning 작성 가이드] ⭐ 중요
behavioral_reasoning은 관찰된 패턴의 타당성을 설명합니다.

"Behavioral: [점수 구간]에서 출발. [관찰된 패턴]. [일관성]. [스트레스 대응]. 따라서 [최종 점수]."

예시 1 (82점):
"Behavioral: 75-89점 구간. 모든 프로젝트 경험(학교 2개, 인턴 1개)에서 일관되게 '완성도'와 '클라이언트 만족' 강조. 비판 반응 수용적 (Segment 5에서 교수님 지적, Segment 9에서 팀장 피드백 모두 긍정적 수용). 자기 귀인 습관 ('내가 부족했다' 3회 언급). 스트레스 대응 양호 (마감 압박 상황 2회, 모두 긍정적 태도). 90-100점 기준(모든 상황에서 완벽한 일관성, 스트레스에도 감사)에는 미달하나 75-89점 충족. 82점."

예시 2 (65점):
"Behavioral: 60-74점 구간. 일부 경험에서 가치관 일관성 부족 (Segment 3에서는 '완성도' 강조, Segment 7에서는 '빨리 끝내는 게 중요' 상충). 비판 반응은 수용적이나 불편함 표출 ('속상했다', '힘들었다'). 스트레스 대응 중간 (압박 상황 회피 언급 1회). 75-89점 기준(대부분 일관)에 미치지 못함. 65점."

───────────────────────────────────────

3️⃣ Critical Perspective (비판적 검증)

[Red Flags 체크리스트]

❌ **방어적 태도** (Severity: Moderate → -10점)
- "내 잘못 아니다", "그 사람이 이해 못했다"
- 비판에 변명

❌ **워라밸 과도 강조** (Severity: Minor → -5점)
- "절대 야근 안 한다", "칼퇴 중요"
- 컨설팅 문화 이해 부족

❌ **낮은 기준** (Severity: Minor → -5점)
- "대충 해도 되지 않나", "80%면 충분"
- 완성도 의식 부족

❌ **타인 귀인** (Severity: Minor → -5점)
- 모든 실패를 "남 탓", "환경 탓"
- 자기 책임 의식 없음

❌ **Resume 불일치** (Severity: Severe → -20점)
- Interview 주장이 Resume에 없음

[Resume 교차 검증]
- 언급한 프로젝트가 Resume에 있는가?
- 피드백 경험이 Resume 기재와 일치하는가?
- 역할(주도 vs 참여)이 일치하는가?

[Critical Reasoning 작성 가이드] ⭐ 중요
critical_reasoning은 발견된 문제와 Resume 검증을 설명합니다.

"Critical: [Red Flags 개수]건 발견. [각 Flag 설명]. Resume 일치도 [점수]. [종합 판단]. 총 감점 [점수]."

예시 1 (-5점):
"Critical: Red Flag 1건. Segment 8에서 '80% 완성도면 충분하다고 생각했다'는 표현, 낮은 기준 의식(-5점). Resume의 'Capstone 프로젝트' 기재와 일치, 교수님 피드백 경험도 Resume에 '논문 지도' 항목 확인. Resume 일치도 0.9. 총 감점 -5점."

예시 2 (-15점):
"Critical: Red Flag 2건. (1) Segment 5에서 '교수님이 너무 까다로워서'라며 비판을 교수님 문제로 귀인, 방어적 태도(-10점). (2) Segment 9에서 '야근은 절대 안 한다' 과도한 워라밸 강조, 컨설팅 문화 이해 부족(-5점). Resume의 프로젝트 기재는 있으나 '팀 우수상' 같은 성과 기재 없어 신뢰도 중간. Resume 일치도 0.7. 총 감점 -15점."

───────────────────────────────────────

═══════════════════════════════════════
 편향 방지 가이드라인
═══════════════════════════════════════

[절대 평가 기준]
- 주니어(0-2년) 기대치로 평가
- "문화 적합성" > "완벽한 경험"
- 신입에게 완벽한 컨설팅 이해는 기대하지 않음

[금지 사항]
❌ 외향성 = 조직 적합성: "밝네" → 가치관 확인
❌ 순종성 = 피드백 수용: "시키는 대로" → 성장 의지 확인
❌ 학벌/전공 우대: "명문대라 적응 잘하겠지" → 실제 답변만
❌ 야근 강요: "야근 각오" 과도 요구 → 압박 대응 능력만 확인

[이 역량 특화 편향 방지]
- 무조건 순종 < 건설적 피드백 수용
- 야근 자랑 < 효율적 압박 대응
- 표면적 밝음 < 진정한 가치관 일치

[신입 기대치]
- 컨설팅 문화 명확히 이해 + 피드백 수용 사례: 우수 (상위 10%)
- 기본적 문화 이해 + 피드백 수용 의지: 평균 이상 (상위 30%)
- 팀워크, 협력 의식: 평균 (상위 50%)

═══════════════════════════════════════
 최종 점수 통합
═══════════════════════════════════════

[통합 공식]

Step 1: Evidence 기준점
base_score = evidence_score
weighted_evidence = base_score × evidence_weight

Step 2: Behavioral 조정
behavioral_gap = behavioral_score - evidence_score
adjustment_factor = 1 + (behavioral_gap / 50)
adjustment_factor = clamp(adjustment_factor, 0.8, 1.2)
adjusted_base = weighted_evidence × adjustment_factor

Step 3: Critical 감점
total_penalties = sum(penalty for each red_flag)
overall_score = adjusted_base + total_penalties
overall_score = clamp(overall_score, 0, 100)

Step 4: Confidence 계산
confidence = (
    evidence_weight × 0.50 +
    resume_match_score × 0.30 +
    (1 - score_variance) × 0.20
)

[계산 예시]
Evidence: 84점, Weight 0.8 (Quote 4개)
Behavioral: 82점
Gap: -2 → Adjustment: 0.96
Adjusted: 84 × 0.8 × 0.96 = 64.5
Critical: -5점
Overall: 64.5 - 5 = 59.5 → 60점
Confidence: (0.8 × 0.5) + (0.9 × 0.3) + (0.85 × 0.2) = 0.84

═══════════════════════════════════════
 입력 데이터
═══════════════════════════════════════

[Interview Transcript]
{transcript}

[Resume]
{resume}

[Transcript 구조 참고]
- TranscriptSegment: segment_id, segment_order로 식별
- question_text: 질문 내용
- answer_text: 지원자 답변 (STT 변환)
- question_type: consulting_fit, behavioral, case_interview, brainteasers
- target_competencies: 이 segment에서 평가할 역량

Quote 추출 시 segment_id와 char_index를 함께 기록하세요.
Consulting Fit 질문을 중심으로 평가하세요.

═══════════════════════════════════════
 출력 형식 (JSON ONLY)
═══════════════════════════════════════

{{
  "competency_name": "organizational_fit",
  "competency_display_name": "조직 적합성",
  "competency_category": "common",
  "evaluated_at": "2025-01-15T10:30:00Z",
  
  "perspectives": {{
    "evidence_score": 84,
    "evidence_weight": 0.8,
    "evidence_details": [
      {{
        "text": "교수님이 만족하실 때까지 5번 수정했고, 그게 당연하다고 생각했어요",
        "segment_id": 4,
        "char_index": 1800,
        "relevance_note": "클라이언트 우선, 높은 기준",
        "quality_score": 0.95
      }},
      {{
        "text": "처음엔 속상했지만, 지적받은 논리 구조를 전면 수정했더니 훨씬 좋아졌어요",
        "segment_id": 6,
        "char_index": 2400,
        "relevance_note": "피드백 수용, 구체적 개선",
        "quality_score": 0.9
      }},
      {{
        "text": "마감 3일 전부터 밤샘했는데, 완성도를 위해서라면 당연하다고 생각해요",
        "segment_id": 8,
        "char_index": 3200,
        "relevance_note": "장시간 근무 긍정적 태도, 완성도 우선",
        "quality_score": 0.9
      }},
      {{
        "text": "좋은 결과는 팀 덕분이고, 부족한 건 제가 더 노력할 부분이에요",
        "segment_id": 10,
        "char_index": 3800,
        "relevance_note": "겸손, 자기 귀인",
        "quality_score": 0.85
      }}
    ],
    "evidence_reasoning": "Evidence: 75-89점(Good) 구간에서 시작. 컨설팅 문화 이해도 중상 (클라이언트 우선 명시 '교수님이 만족할 때까지', 높은 완성도 기준 '당연하다', 마감 압박 경험 '3일 밤샘' + 긍정적 태도). 피드백 수용성 양호 (혹독한 비판 경험 + 긍정적 수용 '처음엔 속상했지만' + 구체적 개선 '논리 구조 전면 수정'). 겸손 ('팀 덕분'). Quote 4개. 90-100점 기준(심각한 비판 + 감사 표현 + 빠른 실행 명시)에는 약간 미달하나 Good 상위권으로 84점 산정.",
    
    "behavioral_score": 82,
    "behavioral_pattern": {{
      "pattern_description": "모든 경험에서 일관된 높은 기준, 비판 수용적, 자기 귀인 습관",
      "specific_examples": [
        "모든 프로젝트(학교 2개, 인턴 1개)에서 일관되게 '완성도'와 '클라이언트 만족' 강조 (Segment 4, 8, 12)",
        "비판 반응 수용적: 교수님 지적(Segment 6), 팀장 피드백(Segment 11) 모두 긍정적 수용",
        "자기 귀인 습관: '내가 부족했다' 3회 언급 (Segment 6, 10, 12)",
        "스트레스 대응 양호: 마감 압박 2회(Segment 8, 12), 모두 긍정적 태도"
      ],
      "consistency_note": "모든 경험에서 일관된 가치관 (클라이언트 우선, 높은 기준)"
    }},
    "behavioral_reasoning": "Behavioral: 75-89점 구간. 모든 프로젝트 경험(학교 2개, 인턴 1개)에서 일관되게 '완성도'와 '클라이언트 만족' 강조. 비판 반응 수용적 (Segment 6에서 교수님 지적, Segment 11에서 팀장 피드백 모두 긍정적 수용). 자기 귀인 습관 ('내가 부족했다' 3회 언급). 스트레스 대응 양호 (마감 압박 상황 2회, 모두 긍정적 태도). 90-100점 기준(모든 상황에서 완벽한 일관성, 비판에 감사)에는 미달하나 75-89점 충족. 82점.",
    
    "critical_penalties": -5,
    "red_flags": [
      {{
        "flag_type": "low_standard",
        "description": "Segment 8에서 '80% 완성도면 충분하다고 생각했었다'는 과거 표현, 현재는 개선되었으나 초기 기준 낮았음",
        "severity": "minor",
        "penalty": -5,
        "evidence_reference": "segment_id: 8, char_index: 3150-3200"
      }}
    ],
    "resume_match_score": 0.9,
    "critical_reasoning": "Critical: Red Flag 1건. Segment 8에서 '80% 완성도면 충분하다고 생각했었다'는 과거 표현, 낮은 기준 의식이었으나 현재는 '100% 완성도' 강조로 개선(-5점). Resume의 'Capstone 프로젝트' 기재와 일치, 교수님 피드백 경험도 Resume에 '논문 지도' 항목 확인. 장시간 근무 경험은 Resume '프로젝트 기간 3개월'과 일치. Resume 일치도 0.9. 총 감점 -5점."
  }},
  
  "overall_score": 60,
  "confidence": {{
    "evidence_strength": 0.8,
    "resume_match": 0.9,
    "internal_consistency": 0.85,
    "overall_confidence": 0.84,
    "confidence_note": "증거 충분(Quote 4개), Resume 일치도 높음(0.9), Evidence-Behavioral 간 편차 2점으로 일관적"
  }},
  
  "calculation": {{
    "base_score": 84,
    "evidence_weight": 0.8,
    "behavioral_adjustment": 0.96,
    "adjusted_base": 64.5,
    "critical_penalties": -5,
    "final_score": 59.5,
    "formula": "84 × 0.8 × 0.96 - 5 = 59.5 → 60점"
  }},
  
  "strengths": [
    "컨설팅 문화 이해도 중상 (클라이언트 우선, 높은 완성도 기준)",
    "피드백 수용성 양호 (비판 경험 + 구체적 개선 사례)",
    "모든 경험에서 일관된 가치관 (완성도, 클라이언트 만족)",
    "장시간 근무에 대한 긍정적 태도 (마감 압박 3일 밤샘)",
    "겸손과 자기 귀인 습관 ('팀 덕분', '내가 부족')"
  ],
  
  "weaknesses": [
    "과거 낮은 기준 의식 (80% 충분, 현재는 개선됨)",
    "비판 수용 시 초기 불편함 표출 ('속상했다')",
    "빠른 실행 의식은 부족 (완성도 우선만 강조)"
  ],
  
  "key_observations": [
    "신입 치고는 컨설팅 문화 이해도가 높음 (상위 30% 추정)",
    "피드백을 성장 기회로 인식하는 성장 마인드",
    "모든 프로젝트에서 일관된 높은 기준 추구",
    "Resume의 '논문 지도', 'Capstone 프로젝트'가 실제 경험과 일치"
  ],
  
  "suggested_followup_questions": [
    "컨설팅 업계의 장시간 근무 문화에 대해 어떻게 생각하시나요?",
    "상사나 클라이언트로부터 혹독한 비판을 받는다면 어떻게 대응하시겠어요?",
    "본인이 생각하는 '완성도 높은 결과물'의 기준은 무엇인가요?"
  ]
}}

═══════════════════════════════════════
⚠️ 중요 알림
═══════════════════════════════════════

1. 반드시 JSON만 출력하세요. 다른 텍스트 금지.
2. segment_id와 char_index를 함께 기록하세요.
3. evidence_reasoning, behavioral_reasoning, critical_reasoning은 필수이며, 점수 구간과 충족/미충족 기준을 명시해야 합니다.
4. 모든 점수는 Quote에 기반해야 합니다.
5. Temperature=0 사용으로 결정성 확보하세요.
6. 신입 기준으로 85점 이상은 매우 드뭅니다 (상위 5%).
7. "문화 적합성" > "완벽한 경험" 우선순위를 유지하세요.
8. Consulting Fit 질문을 중심으로 평가하세요.
"""


def create_organizational_fit_evaluation_prompt(
    transcript: str,
    resume: str
) -> str:
    """
    Organizational Fit Agent 평가 프롬프트 생성
    
    Args:
        transcript: InterviewTranscript의 JSON 문자열
        resume: 파싱된 이력서 텍스트
    
    Returns:
        완성된 프롬프트
    """
    return ORGANIZATIONAL_FIT_PROMPT.format(
        transcript=transcript,
        resume=resume
    )


# 스키마 참조용
EXPECTED_OUTPUT_SCHEMA = {
    "competency_name": "organizational_fit",
    "competency_display_name": "조직 적합성",
    "competency_category": "common",
    "evaluated_at": "datetime",
    "perspectives": {
        "evidence_score": "float (0-100)",
        "evidence_weight": "float (0-1)",
        "evidence_details": [
            {
                "text": "인용구",
                "segment_id": "int",
                "char_index": "int",
                "relevance_note": "관련성 설명",
                "quality_score": "float (0-1)"
            }
        ],
        "evidence_reasoning": "⭐ 점수 구간 + 충족/미충족 기준 + 문화 이해도 + 피드백 수용성",
        "behavioral_score": "float (0-100)",
        "behavioral_pattern": {
            "pattern_description": "가치관 패턴",
            "specific_examples": ["예시1 (segment_id 포함)", "예시2", "일관성"],
            "consistency_note": "일관성"
        },
        "behavioral_reasoning": "⭐ 점수 구간 + 가치관 일관성",
        "critical_penalties": "int (음수)",
        "red_flags": [
            {
                "flag_type": "defensive_attitude/work_life_balance_overemphasis/low_standard/external_attribution/resume_mismatch",
                "description": "구체적 문제",
                "severity": "minor/moderate/severe",
                "penalty": "int (음수)",
                "evidence_reference": "segment_id + char_index"
            }
        ],
        "resume_match_score": "float (0-1)",
        "critical_reasoning": "⭐ Red Flags + Resume 검증"
    },
    "overall_score": "float (0-100)",
    "confidence": {
        "evidence_strength": "float (0-1)",
        "resume_match": "float (0-1)",
        "internal_consistency": "float (0-1)",
        "overall_confidence": "float (0-1)",
        "confidence_note": "종합 설명"
    },
    "calculation": {
        "base_score": "evidence_score",
        "evidence_weight": "0-1",
        "behavioral_adjustment": "0.8-1.2",
        "adjusted_base": "계산 결과",
        "critical_penalties": "int (음수)",
        "final_score": "최종 점수",
        "formula": "계산식 문자열"
    },
    "strengths": ["강점1 (문화 이해도)", "강점2", "강점3", "강점4"],
    "weaknesses": ["약점1", "약점2", "약점3"],
    "key_observations": ["관찰1", "관찰2", "관찰3", "관찰4"],
    "suggested_followup_questions": ["질문1", "질문2", "질문3"]
}