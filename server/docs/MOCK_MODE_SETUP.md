# Mock Mode 구축 문서

##  개요

JD 업로드 및 페르소나 생성 엔드포인트를 Mock 모드로 변경하여 DB 조회/LLM 호출 없이 즉시 응답하도록 구현

**작업 날짜:** 2025-11-20
**대상 엔드포인트:**
- `POST /api/v1/jd-persona/upload`
- `POST /api/v1/jd-persona/generate-persona`

---

## 🔧 수정된 파일

### 1. `/server/utils/s3_uploader.py`
**문제:** Line 10에 incomplete import 구문으로 인한 syntax error

**수정 내용:**
```python
# 수정 전
import datetime
import time
import

# 수정 후
import datetime
import time
```

---

### 2. `/server/services/job_service.py`
**문제:** `_extract_company_weights()` 메서드에서 OpenAI API 호출로 인한 blocking

**수정 내용:** (Lines 94-104)
```python
# 2-1. JD에서 회사 가중치 추출 및 업데이트 (임시 비활성화 - persona_data.json 사용)
print("\n[Step 2-1/6] Skipping company weights extraction (using pre-generated persona_data.json)")
weights_data = None

# 아래 LLM 호출 코드는 OpenAI API 키가 필요하므로 임시 비활성화
# try:
#     weights_data = await self._extract_company_weights(full_text)
# except Exception as e:
#     print(f"  ✗ Failed to extract company weights: {e}")
#     print(f"  → Continuing without weight extraction...")
#     weights_data = None
```

---

### 3. `/server/api/jd_persona.py`

#### 3.1 Import 정리
**추가된 Import:**
```python
import json
from datetime import datetime
```

**제거된 Import:** (중복 Company 문제 회피)
- ~~`from models.job import Job`~~
- ~~`from models.jd_persona import JDPersona`~~

#### 3.2 Upload 엔드포인트 Mock 모드 (Lines 98-127)
```python
# ===== MOCK MODE =====
# PDF 업로드는 받지만, 실제로는 미리 정의된 데이터 반환
# companyId=1 (삼성물산 패션부문), jobId=1 (상품기획/Retail영업)

# Mock 데이터 (DB 조회 없이 hardcoded)
mock_job_id = 1
common_competencies = ["고객지향", "도전정신", "협동·팀워크", "목표지향", "책임감"]
job_competencies = [
    "매출·트렌드 데이터 분석 및 상품 기획 (MD 프로세스)",
    "시즌 전략 수립 및 비즈니스 문제해결 (KPI 관리)",
    "소싱·생산·유통 밸류체인 최적화 (원가·마진 관리)",
    "고객 여정 설계 및 VMD·마케팅 통합 전략",
    "유관부서 협업 및 이해관계자 협상 (디자인/생산/영업)"
]

print(f"✅ Mock 데이터 사용: Job ID={mock_job_id}, 역량 {len(job_competencies)}개")

# 시각화 데이터 생성
competency_service = CompetencyService()
visualization_data = competency_service.get_competency_visualization_data(
    job_competencies=job_competencies
)

return CompetencyAnalysisResponse(
    job_id=mock_job_id,
    common_competencies=common_competencies,
    job_competencies=job_competencies,
    analysis_summary="삼성물산 패션부문 MD/영업 직무 핵심 역량 분석 완료 (Mock)",
    visualization_data=visualization_data
)
```

#### 3.3 Persona 생성 엔드포인트 Mock 모드 (Lines 158-217)
```python
# ===== MOCK MODE =====
# 페르소나 생성 요청을 받지만, 미리 정의된 데이터 반환

# 기업 질문 검증
if len(request.company_questions) != 3:
    raise HTTPException(
        status_code=400,
        detail="Exactly 3 company questions are required"
    )

print(f"❓ Company questions received: {request.company_questions}")

# Mock 페르소나 데이터
mock_company_name = "삼성물산 패션부문"
mock_common_competencies = ["고객지향", "도전정신", "협동·팀워크", "목표지향", "책임감"]
mock_job_competencies = [
    "매출·트렌드 데이터 분석 및 상품 기획 (MD 프로세스)",
    "시즌 전략 수립 및 비즈니스 문제해결 (KPI 관리)",
    "소싱·생산·유통 밸류체인 최적화 (원가·마진 관리)",
    "고객 여정 설계 및 VMD·마케팅 통합 전략",
    "유관부서 협업 및 이해관계자 협상 (디자인/생산/영업)"
]

# 사용자가 입력한 3개 질문 사용
mock_core_questions = request.company_questions

mock_persona_summary = [
    {
        "type": "전략적 사고형 면접관",
        "focus": "시장 분석 및 데이터 기반 의사결정 능력 평가",
        "style": "논리적이고 분석적, 구체적인 근거를 요구",
        "target_competencies": ["매출·트렌드 데이터 분석 및 상품 기획 (MD 프로세스)", "시즌 전략 수립 및 비즈니스 문제해결 (KPI 관리)"]
    },
    {
        "type": "실행력 중심형 면접관",
        "focus": "목표 달성을 위한 창의적 실행과 협업 능력 평가",
        "style": "실무 경험과 구체적 성과를 중시",
        "target_competencies": ["고객 여정 설계 및 VMD·마케팅 통합 전략", "유관부서 협업 및 이해관계자 협상 (디자인/생산/영업)"]
    },
    {
        "type": "글로벌 비즈니스형 면접관",
        "focus": "글로벌 감각과 비즈니스 마인드 평가",
        "style": "전략적 사고와 글로벌 시각을 평가",
        "target_competencies": ["소싱·생산·유통 밸류체인 최적화 (원가·마진 관리)"]
    }
]

print(f"✅ Mock 페르소나 데이터 생성 완료")

return PersonaResponse(
    job_id=request.job_id,
    company=mock_company_name,
    common_competencies=mock_common_competencies,
    job_competencies=mock_job_competencies,
    core_questions=mock_core_questions,
    persona_summary=mock_persona_summary,
    created_at=datetime.now().isoformat()
)
```

---

## 🐛 해결된 문제

### 1. SQLAlchemy Registry Conflict
**오류:**
```
Multiple classes found for path "Company" in the registry of this declarative base.
Please use a fully module-qualified path.
```

**원인:**
- `/server/models/company.py`에 `class Company(Base)` 정의
- `/server/models/interview.py`에 중복 `class Company(Base)` 정의
- 두 모델이 동시에 import되면서 SQLAlchemy registry 충돌

**해결 방법:**
Mock 모드로 전환하여 DB 조회를 완전히 제거함으로써 문제 회피

### 2. Infinite Loading on Upload
**원인:**
- S3 업로드 시도
- Embedding 생성 시도
- LLM API 호출 대기

**해결 방법:**
Hardcoded mock data 반환으로 즉시 응답 (응답 시간: 4.7ms)

---

## ✅ 테스트 결과

### 1. PDF Upload Endpoint
```bash
curl -X POST http://localhost:8000/api/v1/jd-persona/upload \
  -F pdf_file=@/path/to/jd.pdf \
  -F company_id=1 \
  -F title="Test Upload"
```

**응답:**
```json
{
  "job_id": 1,
  "common_competencies": ["고객지향", "도전정신", "협동·팀워크", "목표지향", "책임감"],
  "job_competencies": [
    "매출·트렌드 데이터 분석 및 상품 기획 (MD 프로세스)",
    "시즌 전략 수립 및 비즈니스 문제해결 (KPI 관리)",
    "소싱·생산·유통 밸류체인 최적화 (원가·마진 관리)",
    "고객 여정 설계 및 VMD·마케팅 통합 전략",
    "유관부서 협업 및 이해관계자 협상 (디자인/생산/영업)"
  ],
  "analysis_summary": "삼성물산 패션부문 MD/영업 직무 핵심 역량 분석 완료 (Mock)",
  "visualization_data": { ... }
}
```

**상태:** ✅ 성공 (200 OK, 4.7ms)

### 2. Persona Generation Endpoint
```bash
curl -X POST http://localhost:8000/api/v1/jd-persona/generate-persona \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": 1,
    "company_questions": [
      "삼성물산 패션부문에 지원한 이유는 무엇인가요?",
      "최근 가장 인상 깊게 본 패션 트렌드는 무엇인가요?",
      "팀 협업 시 의견 충돌을 어떻게 해결하시나요?"
    ]
  }'
```

**응답:**
```json
{
  "job_id": 1,
  "company": "삼성물산 패션부문",
  "common_competencies": ["고객지향", "도전정신", "협동·팀워크", "목표지향", "책임감"],
  "job_competencies": [...],
  "core_questions": [
    "삼성물산 패션부문에 지원한 이유는 무엇인가요?",
    "최근 가장 인상 깊게 본 패션 트렌드는 무엇인가요?",
    "팀 협업 시 의견 충돌을 어떻게 해결하시나요?"
  ],
  "persona_summary": [
    {
      "type": "전략적 사고형 면접관",
      "focus": "시장 분석 및 데이터 기반 의사결정 능력 평가",
      ...
    },
    ...
  ],
  "created_at": "2025-11-20T10:30:15.676863"
}
```

**상태:** ✅ 성공 (200 OK)

---

## 🎯 프론트엔드 사용 예시

```javascript
// 1. PDF 업로드
const uploadJD = async (file) => {
  const formData = new FormData();
  formData.append('pdf_file', file);
  formData.append('company_id', 1);
  formData.append('title', '삼성물산 패션부문 채용');

  const response = await fetch('http://localhost:8000/api/v1/jd-persona/upload', {
    method: 'POST',
    body: formData
  });

  const data = await response.json();
  console.log('역량 분석 결과:', data);
  return data;
};

// 2. 페르소나 생성
const generatePersona = async (jobId, questions) => {
  const response = await fetch('http://localhost:8000/api/v1/jd-persona/generate-persona', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      job_id: jobId,
      company_questions: questions
    })
  });

  const data = await response.json();
  console.log('페르소나 생성 결과:', data);
  return data;
};

// 사용 예시
const file = document.querySelector('input[type="file"]').files[0];
const uploadResult = await uploadJD(file);

const personaResult = await generatePersona(uploadResult.job_id, [
  "삼성물산 패션부문에 지원한 이유는 무엇인가요?",
  "최근 가장 인상 깊게 본 패션 트렌드는 무엇인가요?",
  "팀 협업 시 의견 충돌을 어떻게 해결하시나요?"
]);
```

---

## 📝 참고사항

### Mock 데이터 특징
1. **공통 역량 (5개):** 추상적 인성 역량
   - 고객지향, 도전정신, 협동·팀워크, 목표지향, 책임감

2. **직무 역량 (5개):** 구체적 삼성물산 패션부문 MD/영업 역량
   - 매출·트렌드 데이터 분석 및 상품 기획 (MD 프로세스)
   - 시즌 전략 수립 및 비즈니스 문제해결 (KPI 관리)
   - 소싱·생산·유통 밸류체인 최적화 (원가·마진 관리)
   - 고객 여정 설계 및 VMD·마케팅 통합 전략
   - 유관부서 협업 및 이해관계자 협상 (디자인/생산/영업)

3. **면접관 페르소나 (3명):**
   - 전략적 사고형: 데이터 분석, 전략 수립 평가
   - 실행력 중심형: 창의적 실행, 협업 평가
   - 글로벌 비즈니스형: 글로벌 감각, 밸류체인 평가

### 향후 Real Mode 전환 시 고려사항
1. SQLAlchemy Company 중복 정의 문제 해결 필요
   - `models/interview.py`의 Company 클래스 제거 또는 리팩토링
2. OpenAI API 키 설정 필요
3. S3 버킷 및 권한 설정 필요
4. PostgreSQL pgvector extension 설정 필요

---

##  서버 실행 방법

```bash
# 1. 가상환경 활성화
source /home/ec2-user/flex/venv1/bin/activate

# 2. 서버 시작
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 3. Health Check
curl http://localhost:8000/health
```

**서버 로그 확인:**
```bash
tail -f /tmp/backend.log
```

---

## 📚 관련 파일
- `/server/api/jd_persona.py` - 메인 API 엔드포인트
- `/server/services/job_service.py` - Job 처리 서비스
- `/server/utils/s3_uploader.py` - S3 업로드 유틸리티
- `/server/assets/persona_data.json` - 페르소나 템플릿 데이터

---

**작성자:** Claude (AI Assistant)
**최종 수정:** 2025-11-20
