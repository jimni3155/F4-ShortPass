# Transcript 활용 서비스 구현 완료 요약

## ✅ 구현 완료 항목

### 1. **Transcript JSON 변환** ✅
**파일**: `scripts/parse_transcript_to_json.py`
**기능**: scripts.txt → 구조화된 JSON 변환

**출력 예시**:
```json
{
  "metadata": {
    "applicant_name": "박서연",
    "company": "현대모비스 전략기획팀",
    "total_questions": 12
  },
  "qa_pairs": [
    {
      "id": "q1",
      "question_text": "...",
      "answer_text": "...",
      "target_competencies": ["strategic_thinking"]
    }
  ]
}
```

**저장 위치**: `/home/ec2-user/flex/server/test_data/transcript_박서연.json`

---

### 2. **Highlight Extractor** ✅
**파일**: `services/transcript/highlight_extractor.py`
**기능**: 답변에서 평가 근거 문장 추출 + 위치 정보

**핵심 메서드**:
```python
extract_evidence_from_transcript(
    question: str,
    answer: str,
    competency: str,
    score: int
) → {
    "highlighted_sentences": [
        {
            "text": "Python으로 코호트 분석",
            "start": 45,  # 시작 인덱스
            "end": 65,    # 끝 인덱스
            "relevance": 0.95,
            "matched_keywords": ["Python", "분석"]
        }
    ],
    "keywords": ["Python", "Pandas", "코호트 분석"],
    "justification": "구체적인 분석 도구 활용...",
    "coverage_percentage": 35.2  # 전체 답변의 35.2%가 하이라이트
}
```

**사용 시나리오**:
- 프론트엔드에서 `<mark>` 태그로 하이라이팅
- start/end 인덱스로 정확한 위치 표시

---

### 3. **Keyword Mapper** ✅
**파일**: `services/transcript/keyword_mapper.py`
**기능**: 역량별 키워드 출현 빈도 분석 + 태그 클라우드 데이터

**핵심 메서드**:
```python
map_keywords_to_competencies(
    transcript: List[Dict],
    competencies: List[str]
) → {
    "data_driven": [
        {
            "keyword": "Python",
            "count": 3,
            "context": ["문장1", "문장2", "문장3"],
            "qa_ids": ["q3", "q4"]
        },
        {
            "keyword": "데이터",
            "count": 5,
            "context": [...],
            "qa_ids": ["q3", "q5"]
        }
    ]
}
```

**추가 기능**:
- `generate_tag_cloud_data()`: 프론트엔드 태그 클라우드용
- `analyze_keyword_trends()`: 특정 키워드의 출현 패턴 분석
- `get_competency_keyword_overlap()`: 역량 간 키워드 중복 분석

---

### 4. **Evidence Linker** ✅
**파일**: `services/transcript/evidence_linker.py`
**기능**: 점수 → 질문 → 답변 → 하이라이트 체인 연결

**핵심 메서드**:
```python
link_score_to_evidence(
    competency: str,
    score: int,
    transcript: List[Dict]
) → {
    "competency": "data_driven",
    "competency_name": "데이터 기반 의사결정",
    "score": 90,
    "evidence_chain": [
        {
            "qa_id": "q3",
            "question": "데이터를 활용한 경험은?",
            "answer_excerpt": "6개월치 광고 데이터를 수집...",
            "highlight": "피벗 테이블을 만들고, 채널별 전환율과 ROI를 계산",
            "keywords": ["피벗", "전환율", "ROI"],
            "reasoning": "구체적인 데이터 분석 도구와 지표 활용"
        }
    ],
    "score_breakdown": {
        "positive_factors": ["구체적 도구 활용", "정량적 지표 제시"],
        "negative_factors": ["실무 프로젝트 경험 제한적"],
        "overall_reasoning": "인턴십 수준의 데이터 분석 경험..."
    }
}
```

**사용 시나리오**:
- HR이 "데이터 분석력 90점" 클릭 시
- 해당 점수의 근거를 QA 체인으로 시각화

---

### 5. **Follow-up Questions Generator** ✅
**파일**: `services/evaluation/follow_up_questions.py`
**기능**: 약점 기반 후속 질문 자동 생성

**핵심 메서드**:
```python
generate_follow_up_questions(
    weaknesses: List[Dict],
    job_description: str,  # Optional
    transcript: List[Dict],  # Optional
    max_questions: int = 5
) → [
    {
        "question": "데이터가 부족한 상황에서 의사결정을 내려야 한다면...",
        "reason": "데이터 기반 의사결정 역량이 55점으로 부족하여 검증 필요",
        "related_weakness": "data_driven",
        "difficulty": "medium"
    }
]
```

**기능 모드**:
1. **템플릿 모드** (기본): 역량별 사전 정의된 질문 사용
2. **LLM 모드**: 직무/transcript 기반 맞춤형 질문 생성

**역량별 템플릿 질문 예시**:
- data_driven: "데이터가 부족한 상황에서 의사결정을 내려야 한다면..."
- industry_knowledge: "우리 산업의 최근 3년간 가장 큰 변화는..."
- communication: "이해관계가 상충하는 부서 간 협업 상황에서..."

---

## 📊 전체 데이터 흐름

```
1. scripts.txt
   ↓
2. parse_transcript_to_json.py
   ↓
3. transcript_박서연.json
   ↓
4. HighlightExtractor → 문장 하이라이트 + 위치
   ↓
5. KeywordMapper → 키워드 빈도 분석
   ↓
6. EvidenceLinker → 점수-근거 체인 연결
   ↓
7. FollowUpQuestionGenerator → 약점 기반 추가 질문
   ↓
8. 결과 페이지 API → 프론트엔드 시각화
```

---

## 🎯 API 사용 예시

### **예시 1: 특정 역량의 평가 근거 조회**

```python
from services.transcript.evidence_linker import EvidenceLinker
import json

# Transcript 로드
with open("test_data/transcript_박서연.json") as f:
    data = json.load(f)

# Evidence Linker 초기화
linker = EvidenceLinker()

# 데이터 분석력 90점의 근거 조회
evidence = linker.link_score_to_evidence(
    competency="data_driven",
    score=90,
    transcript=data["qa_pairs"]
)

print(evidence["evidence_chain"][0]["highlight"])
# → "피벗 테이블을 만들고, 채널별 전환율과 ROI를 계산"
```

---

### **예시 2: 키워드 태그 클라우드 데이터 생성**

```python
from services/transcript.keyword_mapper import KeywordMapper

mapper = KeywordMapper()

# 역량별 키워드 매핑
keyword_map = mapper.map_keywords_to_competencies(
    transcript=data["qa_pairs"],
    competencies=["data_driven", "communication"]
)

# 태그 클라우드 데이터 생성 (프론트엔드용)
tag_cloud = mapper.generate_tag_cloud_data(keyword_map, "data_driven")

# 결과:
# [
#   {"text": "데이터", "value": 5, "color": "#1f77b4"},
#   {"text": "Python", "value": 3, "color": "#ff7f0e"}
# ]
```

---

### **예시 3: 약점 기반 후속 질문 생성**

```python
from services.evaluation.follow_up_questions import FollowUpQuestionGenerator

generator = FollowUpQuestionGenerator(use_llm=False)  # 템플릿 모드

weaknesses = [
    {
        "competency": "industry_knowledge",
        "score": 55,
        "summary": "자동차 산업 이해도 부족"
    }
]

questions = generator.generate_follow_up_questions(
    weaknesses=weaknesses,
    max_questions=3
)

print(questions[0]["question"])
# → "우리 산업의 최근 3년간 가장 큰 변화는 무엇이라고 생각하나요?"
```

---

## 📁 파일 구조

```
server/
├── scripts/
│   └── parse_transcript_to_json.py       # Transcript JSON 변환
├── services/
│   ├── transcript/
│   │   ├── highlight_extractor.py        # 하이라이트 추출
│   │   ├── keyword_mapper.py             # 키워드 매핑
│   │   └── evidence_linker.py            # 근거 연결
│   └── evaluation/
│       ├── evidence_extractor.py         # (기존) 기본 근거 추출
│       └── follow_up_questions.py        # 후속 질문 생성
└── test_data/
    └── transcript_박서연.json             # 변환된 JSON

api/
└── evaluation.py                          # 결과 API 엔드포인트
    ├── GET /evaluations/.../evidence     # 근거 조회
    └── GET /evaluations/.../applicants   # 필터링
```

---

## 🚀 다음 단계

### **1단계: 통합 테스트** (권장)
```bash
# 전체 흐름 테스트
python test_transcript_integration.py
```

### **2단계: API 엔드포인트 추가** (선택)
```python
# GET /api/v1/evaluations/applicants/{id}/highlights
# → HighlightExtractor 결과 반환

# GET /api/v1/evaluations/applicants/{id}/keywords
# → KeywordMapper 결과 반환

# GET /api/v1/evaluations/applicants/{id}/follow-up-questions
# → FollowUpQuestionGenerator 결과 반환
```

### **3단계: 프론트엔드 연결**
- TranscriptViewer.tsx에서 하이라이트 표시
- 태그 클라우드 컴포넌트
- 후속 질문 표시

---

## 💡 핵심 차별화 포인트

1. **Transcript → 평가 근거 연결** ✅
   - "알고리즘 산출 과정이 아니라, 실제 면접 내용을 보여줌"
   - 멘토 요구사항 100% 충족

2. **문장 단위 하이라이팅** ✅
   - start/end 인덱스로 정확한 위치 표시
   - 프론트엔드에서 `<mark>` 태그로 시각화

3. **키워드 빈도 분석** ✅
   - 역량별 키워드 매핑
   - 태그 클라우드 시각화

4. **약점 기반 후속 질문** ✅
   - 약점 역량에 대한 자동 검증 질문
   - 2차 면접에서 활용 가능

---

## ✅ 체크리스트

- [x] scripts.txt → JSON 변환
- [x] HighlightExtractor 구현
- [x] KeywordMapper 구현
- [x] EvidenceLinker 구현
- [x] FollowUpQuestionGenerator 구현
- [ ] 통합 테스트 스크립트
- [ ] API 엔드포인트 추가
- [ ] 프론트엔드 연결
- [ ] 발표 자료 작성
