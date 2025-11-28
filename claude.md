# 지원자 평가 페이지 구현 문서

## 개요
AI 면접 평가 결과를 확인할 수 있는 지원자 목록 및 상세 페이지 구현

---

## 1. 구현된 기능

### 1.1 Backend API (`/server/api/evaluation_list.py`)

#### Endpoint 1: 지원자 목록 조회
```
GET /api/v1/evaluations/jobs/{job_id}/applicants
```

**Response:**
```json
{
  "job_id": 2,
  "applicants": [
    {
      "evaluation_id": 3,
      "applicant_id": 2,
      "applicant_name": "윤지원",
      "overall_score": 88.5,
      "normalized_score": 92.0,
      "created_at": "2024-01-15T10:30:00"
    }
  ],
  "total_count": 3
}
```

#### Endpoint 2: 지원자 상세 평가 결과
```
GET /api/v1/evaluations/jobs/{job_id}/applicants/{applicant_id}/result
```

**Response:**
```json
{
  "evaluation_id": 3,
  "applicant_id": 2,
  "applicant_name": "윤지원",
  "overall_score": 88.5,
  "normalized_score": 92.0,
  "confidence_score": 0.92,
  "competency_scores": {
    "job_expertise": 65.0,
    "analytical": 70.0,
    "execution": 85.0,
    "relationship": 95.0,
    "resilience": 92.0,
    "influence": 88.0
  },
  "reasoning_log": {
    "communication": {
      "score": 90,
      "reasoning": "명확하고 효과적인 의사소통 능력",
      "strengths": ["경청 능력", "명확한 표현"],
      "weaknesses": ["전문 용어 사용 부족"]
    }
  },
  "aggregated_evaluation": {
    "recommendation": "STRONG_FIT",
    "overall_feedback": "스펙은 다소 부족하나 핵심 가치에 완벽히 부합하는 숨은 인재"
  },
  "match_result": {
    "key_strengths": ["고객 중심 사고", "빠른 학습 능력"],
    "key_concerns": ["직무 경험 부족"]
  }
}
```

#### Endpoint 3: Job 통계
```
GET /api/v1/evaluations/jobs/{job_id}/statistics
```

---

### 1.2 Frontend Pages

#### Page 1: CandidateListPage (`/client/src/pages/CandidateListPage.jsx`)

**Route:** `/company/applicants/:jobId`

**기능:**
- 해당 Job의 모든 지원자 목록 표시
- 종합 점수(overall_score) 기준 내림차순 정렬
- 순위, 이름, 점수 표시
- 행 클릭 시 상세 페이지로 이동

**UI 구성:**
```
┌─────────────────────────────────────────────┐
│ 지원자 평가 목록                              │
│ Job ID: 2 | 총 3명                           │
├─────┬─────────┬──────────┬──────────┬───────┤
│순위 │ 이름     │ 종합점수 │ 표준화점수│ 액션  │
├─────┼─────────┼──────────┼──────────┼───────┤
│ #1  │ 윤지원   │   88.5   │   92.0   │ 상세→ │
│ #2  │ 윤       │   75.0   │   78.0   │ 상세→ │
│ #3  │ 홍길동   │   72.5   │   75.0   │ 상세→ │
└─────┴─────────┴──────────┴──────────┴───────┘
```

#### Page 2: CandidateDetailPage (`/client/src/pages/CandidateDetailPage.jsx`)

**Route:** `/company/applicants/:jobId/:applicantId`

**기능:**
- 지원자의 상세 평가 결과 표시
- 종합 점수 3가지 (Overall, Normalized, Confidence)
- 6개 직무 역량 점수 + 프로그레스 바
- 6개 공통 역량 상세 분석 (reasoning, strengths, weaknesses)
- 핵심 인사이트 (강점/개선 영역)
- 종합 평가 및 추천 등급

**UI 구성:**
```
┌─────────────────────────────────────────────┐
│ ← 목록으로 돌아가기                           │
│ 윤지원 - 상세 평가                            │
├─────────────────────────────────────────────┤
│ 종합 점수                                     │
│  88.5        92.0         0.92              │
│ Overall   Normalized   Confidence           │
├─────────────────────────────────────────────┤
│ 종합 평가                                     │
│ [STRONG_FIT]                                │
│ 스펙은 다소 부족하나 핵심 가치에 완벽히 부합   │
├─────────────────────────────────────────────┤
│ 직무 역량 점수 (6개)                          │
│ ┌───────────────────┬─────┐                │
│ │ Job Expertise     │  65 │ ████░░░░░░     │
│ │ Analytical        │  70 │ █████░░░░░     │
│ │ Execution         │  85 │ ██████████     │
│ │ Relationship      │  95 │ ███████████    │
│ │ Resilience        │  92 │ ██████████     │
│ │ Influence         │  88 │ █████████░     │
│ └───────────────────┴─────┘                │
├─────────────────────────────────────────────┤
│ 공통 역량 상세 (6개)                          │
│ ▌Communication                        90   │
│ ▌명확하고 효과적인 의사소통 능력             │
│ ▌강점: 경청 능력, 명확한 표현                │
│ ▌약점: 전문 용어 사용 부족                   │
├─────────────────────────────────────────────┤
│ 핵심 인사이트                                 │
│ 주요 강점          │ 개선 필요 영역           │
│ • 고객 중심 사고    │ • 직무 경험 부족        │
│ • 빠른 학습 능력    │                         │
└─────────────────────────────────────────────┘
```

---

### 1.3 Routes (`/client/src/App.jsx`)

```jsx
import CandidateListPage from '@pages/CandidateListPage';
import CandidateDetailPage from '@pages/CandidateDetailPage';

const router = createBrowserRouter(
  createRoutesFromElements(
    <Route path='/' element={<Layout />}>
      {/* 기존 routes... */}
      <Route path='/company/applicants/:jobId' element={<CandidateListPage />} />
      <Route path='/company/applicants/:jobId/:applicantId' element={<CandidateDetailPage />} />
    </Route>
  )
);
```

---

## 2. 테스트 데이터

### Job ID: 2
**Job Title:** Product Manager - AI Platform

### 지원자 3명

#### 1. 지원자 A - 홍길동 (applicant_id: 1)
- **Overall Score:** 72.5
- **케이스:** 스펙 우수 A형 (높은 스펙, 낮은 가치 부합도)
- **특징:**
  - Job Expertise: 95점 (매우 높음)
  - Relationship: 55점 (낮음)
  - 고객 중심 사고 부족
- **추천:** CONDITIONAL_FIT

#### 2. 지원자 B - 윤지원 (applicant_id: 2) ⭐ 숨은 인재
- **Overall Score:** 88.5 (최고점)
- **케이스:** 가치 부합 B형 (낮은 스펙, 높은 가치 부합도)
- **특징:**
  - Job Expertise: 65점 (낮음)
  - Relationship: 95점 (매우 높음)
  - 고객 중심 사고 탁월
  - 빠른 학습 능력
- **추천:** STRONG_FIT (강력 추천)

#### 3. 지원자 C - 윤 (applicant_id: 3)
- **Overall Score:** 75.0
- **케이스:** 평범한 수준
- **추천:** MODERATE_FIT

---

## 3. 핵심 컨셉: Flex Mentor Feedback Strategy

### "스펙 좋은 A vs 가치 맞는 B" 시나리오

이 평가 시스템은 **3개의 독립적인 AI Agent**가 협업하여 지원자를 평가:

1. **Spec Matching Agent** - 직무 스펙 매칭
2. **Customer Focus Agent** - 고객 중심 사고
3. **Learning Attitude Agent** - 학습 태도 및 성장 가능성

### 핵심 인사이트
- 높은 스펙 ≠ 최고의 인재
- 숨은 인재(B형) 발견: 스펙은 부족하지만 핵심 가치에 완벽히 부합
- 다차원 평가: 6개 직무역량 + 6개 공통역량

---

## 4. 접속 방법

### 개발 서버 실행

**Backend:**
```bash
cd /home/ec2-user/flex/server
source venv1/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd /home/ec2-user/flex/client
npm run dev
```

### 접속 URL

#### 지원자 목록 페이지
```
http://localhost:5173/company/applicants/2
```

#### 지원자 상세 페이지
```
# 윤지원 (숨은 인재 케이스)
http://localhost:5173/company/applicants/2/2

# 홍길동 (높은 스펙 케이스)
http://localhost:5173/company/applicants/2/1

# 윤 (평범한 케이스)
http://localhost:5173/company/applicants/2/3
```

---

## 5. API 테스트

### cURL 명령어

```bash
# 1. 지원자 목록 조회
curl http://localhost:8000/api/v1/evaluations/jobs/2/applicants

# 2. 윤지원 상세 조회
curl http://localhost:8000/api/v1/evaluations/jobs/2/applicants/2/result

# 3. Job 통계
curl http://localhost:8000/api/v1/evaluations/jobs/2/statistics
```

---

## 6. 데이터 구조

### 6개 직무 역량 (Competency Scores)
1. `job_expertise` - 직무 전문성
2. `analytical` - 분석적 사고
3. `execution` - 실행력
4. `relationship` - 관계 구축
5. `resilience` - 회복탄력성
6. `influence` - 영향력

### 6개 공통 역량 (Reasoning Log)
1. `communication` - 의사소통
2. `problem_solving` - 문제 해결
3. `learning_attitude` - 학습 태도
4. `collaboration` - 협업
5. `adaptability` - 적응력
6. `initiative` - 주도성

### Reasoning Log 구조
```json
{
  "communication": {
    "score": 90,
    "reasoning": "평가 근거",
    "strengths": ["강점1", "강점2"],
    "weaknesses": ["약점1"]
  }
}
```

---

## 7. 기술 스택

### Backend
- FastAPI
- SQLAlchemy (Raw SQL)
- PostgreSQL
- Python 3.x

### Frontend
- React 18
- Vite
- React Router v6
- Tailwind CSS

### API Design
- RESTful API
- JSON Response
- CORS 설정 완료

---

## 8. 주요 특징

### Raw SQL 사용 이유
- SQLAlchemy ORM 모델 복잡도 회피
- 빠른 구현 및 디버깅
- 직접적인 데이터베이스 쿼리 제어

### UI/UX 특징
- 반응형 디자인 (Tailwind CSS)
- 직관적인 네비게이션
- 시각적 피드백 (프로그레스 바, 배지)
- 로딩/에러 상태 처리

### 데이터 시각화
- 점수별 색상 구분 (Blue, Green, Purple)
- 프로그레스 바로 역량 수준 표시
- 강점/약점 명확한 구분 (Green/Red)

---

## 9. 향후 개선 사항

### 기능 추가
- [ ] 필터링 기능 (점수 범위, 추천 등급)
- [ ] 정렬 옵션 (이름, 점수, 날짜)
- [ ] 검색 기능
- [ ] 비교 기능 (여러 지원자 동시 비교)
- [ ] PDF 내보내기
- [ ] 차트 시각화 (레이더 차트)

### 성능 개선
- [ ] 페이지네이션
- [ ] 무한 스크롤
- [ ] 데이터 캐싱
- [ ] API 응답 최적화

### UI/UX 개선
- [ ] 애니메이션 효과
- [ ] 다크 모드
- [ ] 반응형 개선 (모바일)
- [ ] 접근성 향상 (ARIA)

---

## 10. 파일 구조

```
flex/
├── server/
│   ├── main.py                          # FastAPI 앱, 라우터 등록
│   ├── api/
│   │   └── evaluation_list.py           # 평가 API 엔드포인트
│   └── db/
│       └── database.py                  # DB 연결 설정
│
├── client/
│   ├── src/
│   │   ├── App.jsx                      # 라우트 설정
│   │   ├── pages/
│   │   │   ├── CandidateListPage.jsx   # 지원자 목록 페이지
│   │   │   └── CandidateDetailPage.jsx # 지원자 상세 페이지
│   │   └── layout/
│   │       └── Layout.jsx               # 공통 레이아웃
│   └── package.json
│
└── claude.md                            # 본 문서
```

---

## 11. 문제 해결 이력

### Issue 1: ERR_CONNECTION_REFUSED
- **원인:** 평가 API 엔드포인트 미존재
- **해결:** evaluation_list.py 생성, main.py에 라우터 등록

### Issue 2: SQLAlchemy 모델 충돌
- **원인:** relationship 필드명 충돌, 컬럼 누락
- **해결:** Raw SQL 사용으로 우회

### Issue 3: 파일 삭제 (git clean)
- **원인:** git clean으로 untracked 파일 삭제
- **해결:** 간소화된 버전으로 재구현

---

## 12. 참고 문서

- FLEX_MENTOR_FEEDBACK_STRATEGY.md - 평가 전략
- DOCUMENTATION_INDEX.md - 전체 문서 인덱스
- 방향정리.md - 서비스 방향성

---

**작성일:** 2025-11-19
**작성자:** Claude Code Assistant
**버전:** 1.0.0

---

## 13. JSON 샘플 파일 (2025-11-22 추가)

### 채아에게 전달할 공식 샘플 파일들

#### 파일 위치
```
/server/test_data/
├── transcript_official_sample.json   # 면접 transcript 형식
├── evaluation_response_sample.json   # 평가 결과 형식
├── transcript_top_sample.json        # 좋은 지원자 케이스
└── transcript_bottom_sample.json     # 약한 지원자 케이스
```

---

### 13.1 Transcript 공식 형식 (`transcript_official_sample.json`)

```json
{
  "company_id": 1,
  "company_name": "삼성물산 패션부문",
  "job_id": 1,
  "job_title": "상품기획/리테일 영업(MD)",
  "applicant_id": 101,
  "applicant_name": "김지원",
  "interview_id": 90001,
  "persona_id": "SAMSUNG_FASHION_MD",
  "persona_meta": {
    "name": "삼성물산 패션부문 시니어 면접관",
    "tone": "전문적/압박",
    "focus": ["데이터 기반 의사결정", "실행력", "협업"]
  },
  "weights": {
    "category": { "common_competencies": 0.5, "job_competencies": 0.5 },
    "competency": {
      "COMM_01": 0.2, "COMM_02": 0.2, "COMM_03": 0.2, "COMM_04": 0.2, "COMM_05": 0.2,
      "JOB_01": 0.2, "JOB_02": 0.2, "JOB_03": 0.2, "JOB_04": 0.2, "JOB_05": 0.2
    }
  },
  "source": {
    "stt_provider": "mock_ws_stream",
    "transcript_version": "v1",
    "collected_at": "2025-11-22T04:00:00Z"
  },
  "segments": [
    {
      "segment_id": 1,
      "segment_order": 1,
      "turn_type": "main",
      "question_text": "질문 내용",
      "answer_text": "답변 내용",
      "answer_duration_sec": 78,
      "char_index_start": 0,
      "char_index_end": 272,
      "timestamp_start": "2025-11-22T04:00:10Z",
      "timestamp_end": "2025-11-22T04:01:28Z"
    }
  ],
  "highlights": {
    "top_segments": [{ "segment_id": 1, "reason": "좋은 이유" }],
    "under_segments": [{ "segment_id": 3, "reason": "보완 필요 이유" }]
  }
}
```

---

### 13.2 평가 결과 형식 (`evaluation_response_sample.json`)

```json
{
  "interview_id": 90001,
  "applicant_id": 101,
  "applicant_name": "김지원",
  "job_id": 1,
  "job_title": "상품기획/리테일 영업(MD)",
  "company_id": 1,
  "persona_id": "SAMSUNG_FASHION_MD",
  "weights": { ... },
  "scores": {
    "job_overall": 89.2,
    "common_overall": 84.5,
    "final_score": 87.0,
    "confidence_overall": 0.81,
    "reliability_level": "high"
  },
  "competencies": [
    {
      "id": "JOB_01",
      "name": "매출·트렌드 데이터 분석 및 상품 기획",
      "category": "job",
      "score": 92,
      "confidence": { "overall": 0.83, "evidence_strength": 0.82 },
      "strengths": ["강점1", "강점2"],
      "weaknesses": ["약점1"],
      "evidence_segments": [1]
    }
  ],
  "analysis_summary": {
    "aggregator_summary": "종합 평가 요약",
    "overall_applicant_summary": "지원자 전체 요약",
    "positive_keywords": ["키워드1", "키워드2"],
    "negative_keywords": ["키워드3"],
    "recommended_questions": ["추천 질문1", "추천 질문2"]
  },
  "evidence": {
    "transcript_s3_key": "logs/evaluations/101/90001/transcript.json",
    "execution_logs": [...]
  },
  "ui_defaults": {
    "detail_tabs": ["요약", "역량별", "추천질문"],
    "badges": ["high_confidence", "data_driven"]
  }
}
```

---

### 13.3 역량 정의 (공통 5개 + 직무 5개)

#### 공통 역량 (COMM_01 ~ COMM_05)

| ID | Key | 이름 |
|----|-----|------|
| COMM_01 | problem_solving | Problem Solving (문제해결력) |
| COMM_02 | achievement_motivation | Achievement Motivation (성취/동기 역량) |
| COMM_03 | growth_potential | Growth Potential (성장 잠재력) |
| COMM_04 | interpersonal_skill | Interpersonal Skill (대인관계 역량) |
| COMM_05 | organizational_fit | Organizational Fit (조직 적합성) |

#### 직무 역량 (JOB_01 ~ JOB_05)

| ID | Key | 이름 |
|----|-----|------|
| JOB_01 | data_insight | Data-Driven Insight (데이터 기반 인사이트) |
| JOB_02 | strategic_problem_solving | Strategic Problem Solving (전략적 문제해결) |
| JOB_03 | value_chain_optimization | Value Chain Optimization (밸류체인 최적화) |
| JOB_04 | customer_journey_marketing | Customer Journey & Marketing (고객 여정/마케팅) |
| JOB_05 | stakeholder_management | Stakeholder Management (이해관계자 관리) |

---

### 13.4 페르소나 JSON 위치

```
/server/assets/
├── persona_data.json              # 공식 페르소나 (공통5 + 직무5)
└── persona_samsung_fashion.json   # 삼성물산 패션부문 전용
```

---

### 13.5 기업 화면 흐름 (PersonaGeneration)

```
1. JD 업로드 → /api/v1/jd-persona/upload
   - PDF 업로드
   - 직무 역량 5개 반환 (persona_data.json 기반)

2. 가중치 설정 → WeightPentagonDraggable
   - 드래그로 각 역량 가중치 조정
   - 합계 100% 자동 정규화

3. 페르소나 생성 → /api/v1/jd-persona/generate-persona
   - 기업 질문 3개 입력
   - 페르소나 3가지 타입 반환
```

---

**업데이트:** 2025-11-22
**버전:** 1.1.0

---

## 14. 면접 시스템 V4 (2025-11-22 추가)

### 14.1 3인 면접관 순차 면접 시스템

#### 핵심 기능
- 3명의 면접관이 순차적으로 면접 진행
- 각 면접관별 다른 역량 평가 포커스
- 이력서 기반 맞춤 질문 지원
- WebSocket 기반 실시간 음성 면접

#### 면접관 구성 (`persona_samsung_fashion.json`)

| ID | 이름 | 유형 | 평가 포커스 |
|----|------|------|-------------|
| INT_01 | 김전략 수석 | 전략형 | 데이터 기반 의사결정, 상품 포트폴리오 |
| INT_02 | 박협업 팀장 | 실행형 | 유관부서 협업, 갈등 조율 |
| INT_03 | 이컬처 매니저 | 조직적합형 | 조직 적합성, 학습 민첩성 |

---

### 14.2 파일 구조

```
/server/
├── services/
│   └── interview_service_v4.py      # 3인 면접관 순차 면접 서비스
├── assets/
│   └── persona_samsung_fashion.json # 3인 면접관 페르소나 정의
└── test_data/
    ├── interview_questions_101.json # 김지원 이력서 기반 질문
    ├── resume_sample_101.json       # 김지원 이력서 (우수 지원자)
    └── resume_sample_1002.json      # 이민수 이력서 (약한 지원자)
```

---

### 14.3 WebSocket 메시지 흐름

```
클라이언트                           서버
    │                                 │
    │─────── WebSocket 연결 ─────────>│
    │<────── connection_success ──────│
    │<────── interview_info ──────────│  (면접관 3명 정보)
    │                                 │
    │─────── start_interview ────────>│
    │<────── ack_start ───────────────│
    │                                 │
    │    [면접관 1: 김전략 수석]        │
    │<────── interviewer_change ──────│
    │<────── question_audio ──────────│  (질문 1)
    │─────── PCM audio bytes ────────>│
    │─────── answer_end ─────────────>│
    │<────── stt_final ───────────────│
    │        (질문 2~N 반복)            │
    │<────── interviewer_complete ────│
    │                                 │
    │    [면접관 2: 박협업 팀장]        │
    │<────── interviewer_change ──────│
    │        (질문/답변 반복)           │
    │<────── interviewer_complete ────│
    │                                 │
    │    [면접관 3: 이컬처 매니저]       │
    │<────── interviewer_change ──────│
    │        (질문/답변 반복)           │
    │<────── interviewer_complete ────│
    │                                 │
    │<────── interview_end ───────────│  (결과 JSON URL)
```

---

### 14.4 핵심 메시지 타입

#### 서버 → 클라이언트

| 타입 | 설명 |
|------|------|
| `connection_success` | WebSocket 연결 성공 |
| `interview_info` | 전체 면접관 정보 (3명) |
| `ack_start` | 면접 시작 확인 |
| `interviewer_change` | 면접관 전환 알림 |
| `question_audio` | 질문 (텍스트 + TTS 오디오 URL) |
| `question_end` | 질문 전송 완료 |
| `stt_final` | STT 변환 결과 |
| `interviewer_complete` | 해당 면접관 면접 종료 |
| `interview_end` | 전체 면접 종료 + 결과 URL |

#### 클라이언트 → 서버

| 타입 | 설명 |
|------|------|
| `start_interview` | 면접 시작 요청 |
| `answer_end` | 답변 종료 신호 |
| (binary) | PCM16 오디오 데이터 |

---

### 14.5 이력서 기반 맞춤 질문

#### 질문 파일 형식 (`interview_questions_{applicant_id}.json`)

```json
{
  "applicant_id": 101,
  "applicant_name": "김지원",
  "resume_summary": {
    "current_position": "MD (한섬, 여성 캐주얼 사업부)",
    "experience_years": 4.5,
    "key_achievements": ["재고회전율 50% 향상", "마진율 3.5%p 개선"],
    "strengths": ["데이터 기반 의사결정", "이해관계자 조율"],
    "weaknesses": ["리스크 관리 체계화 부족"]
  },
  "interviewers": [
    {
      "id": "INT_01",
      "name": "김전략 수석",
      "type": "전략형",
      "resume_based_questions": [
        {
          "question": "재고회전율을 0.8에서 1.2로 50% 개선하셨다고 했는데...",
          "intent": "데이터 분석력 + 트레이드오프 인식 검증",
          "related_resume": "재고회전율 개선 프로젝트",
          "follow_up_if_weak": "회전율만 높이면 품절 리스크가 있을 텐데..."
        }
      ]
    }
  ]
}
```

#### 병합 로직

1. `interview_service_v4.py`가 `interview_questions_{applicant_id}.json` 로드
2. 각 면접관 ID 매칭 (INT_01, INT_02, INT_03)
3. `resume_based_questions` → 기존 `questions` 교체
4. `follow_up_if_weak` → `follow_ups` dict에 저장

---

### 14.6 테스트 방법

#### 1. 서버 실행
```bash
cd /home/ec2-user/flex/server
source ../venv1/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. WebSocket 연결 (wscat)
```bash
wscat -c ws://localhost:8000/api/v1/interviews/101/ws?applicant_id=101
```

#### 3. 면접 시작
```json
{"type": "start_interview"}
```

---

### 14.7 이력서 샘플

#### 우수 지원자 - 김지원 (applicant_id: 101)

| 항목 | 내용 |
|------|------|
| 현재 직책 | MD (한섬, 여성 캐주얼 사업부) |
| 경력 | 4.5년 |
| 핵심 성과 | 재고회전율 50%↑, 마진율 3.5%p↑ |
| 강점 | 데이터 기반 의사결정, 이해관계자 조율 |
| 약점 | 리스크 관리 체계화, 글로벌 소싱 경험 |

#### 약한 지원자 - 이민수 (applicant_id: 1002)

| 항목 | 내용 |
|------|------|
| 현재 직책 | (신입, 인턴 경험만) |
| 경력 | 인턴 6개월 |
| 핵심 성과 | 정량적 성과 없음 |
| 강점 | 성실함, 팀워크 |
| 약점 | 데이터 분석 경험 부족, 리더십 경험 없음 |

---

## 15. MAS (Multi-Agent System) 아키텍처

### 15.1 현재 구조

```
┌─────────────────────────────────────────────────────────────┐
│                    LangGraph Orchestrator                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │ Competency  │    │ Competency  │    │ Competency  │     │
│  │ Agent #1    │    │ Agent #2    │    │ Agent #10   │     │
│  │ (COMM_01)   │    │ (COMM_02)   │ .. │ (JOB_05)    │     │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘     │
│         │                  │                  │             │
│         └──────────────────┼──────────────────┘             │
│                            ▼                                │
│                  ┌─────────────────┐                        │
│                  │   Aggregator    │                        │
│                  │     Node        │                        │
│                  └────────┬────────┘                        │
│                           ▼                                 │
│                  ┌─────────────────┐                        │
│                  │ Final Integration│                       │
│                  │      Node        │                       │
│                  └─────────────────┘                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 15.2 에이전트 구성

#### 공통 역량 에이전트 (5개)
| ID | 에이전트 | 평가 항목 |
|----|----------|-----------|
| COMM_01 | Problem Solving Agent | 문제해결력 |
| COMM_02 | Achievement Motivation Agent | 성취/동기 역량 |
| COMM_03 | Growth Potential Agent | 성장 잠재력 |
| COMM_04 | Interpersonal Skill Agent | 대인관계 역량 |
| COMM_05 | Organizational Fit Agent | 조직 적합성 |

#### 직무 역량 에이전트 (5개)
| ID | 에이전트 | 평가 항목 |
|----|----------|-----------|
| JOB_01 | Data Analysis Agent | 데이터 기반 인사이트 |
| JOB_02 | Strategic Problem Solving Agent | 전략적 문제해결 |
| JOB_03 | Value Chain Optimization Agent | 밸류체인 최적화 |
| JOB_04 | Customer Journey Marketing Agent | 고객 여정/마케팅 |
| JOB_05 | Stakeholder Management Agent | 이해관계자 관리 |

### 15.3 AWS Step Functions 사용 여부

**결론: 현재 불필요**

| 고려 사항 | 현재 상태 | Step Functions 필요? |
|-----------|-----------|---------------------|
| 실행 시간 | 1-5분 | X (15분 미만) |
| 워크플로우 | LangGraph로 관리 | X (이미 해결) |
| Human-in-the-loop | 없음 (자동화) | X |
| AWS 서비스 연계 | 단일 서버 | X |
| 실행 이력 | DB 로깅 | X |

**향후 고려 시점:**
- 동시 평가 100건+ 배치 처리
- HR 담당자 중간 승인 프로세스 추가
- S3 → Lambda → DynamoDB 서비스 체인 구축

---

## 16. Mock 모드 설정

### 16.1 현재 Mock 설정

| 항목 | Mock 값 | 파일 위치 |
|------|---------|-----------|
| 페르소나 | 삼성물산 패션부문 | `/server/assets/persona_samsung_fashion.json` |
| 지원자 | 김지원 (ID: 101) | `/server/test_data/resume_sample_101.json` |
| 질문 리스트 | 이력서 기반 6개 | `/server/test_data/interview_questions_101.json` |
| WebSocket URL | `?applicant_id=101` | `/client/src/pages/AIInterview.jsx:159` |

### 16.2 테스트 흐름

```
프론트엔드 면접 시작 버튼
        │
        ▼
WebSocket 연결 (?applicant_id=101)
        │
        ▼
interview_service_v4.py
├── _load_persona_data() → persona_samsung_fashion.json
├── _get_interviewers() → 3명 면접관
├── _load_resume_questions(101) → interview_questions_101.json
└── _merge_resume_questions() → 이력서 기반 질문 병합
        │
        ▼
3인 면접관 순차 면접 진행
```

---

**버전:** 1.3.0
**업데이트:** 2025-11-22

---

## 17. 작업 이력 (2025-11-22)

### 17.1 면접 시스템 V4 구현

#### 완료된 작업

| 작업 | 파일 | 설명 |
|------|------|------|
| 3인 면접관 페르소나 정의 | `persona_samsung_fashion.json` | 전략형/실행형/조직적합형 3명 |
| 이력서 샘플 생성 | `resume_sample_101.json` | 김지원 (우수 지원자) |
| 이력서 샘플 생성 | `resume_sample_1002.json` | 이민수 (약한 지원자) |
| 이력서 기반 질문 생성 | `interview_questions_101.json` | 김지원 맞춤 질문 6개 |
| 면접 서비스 수정 | `interview_service_v4.py` | 3인 순차 면접 + 이력서 질문 병합 |
| API 수정 | `interview.py` | `applicant_id` 쿼리 파라미터 추가 |
| 프론트 Mock 설정 | `AIInterview.jsx` | `?applicant_id=101` 하드코딩 |

#### 새로 추가된 함수 (`interview_service_v4.py`)

```python
def _load_resume_questions(self, applicant_id: int)
    # interview_questions_{applicant_id}.json 로드

def _merge_resume_questions(self, interviewers, resume_data)
    # 페르소나 면접관에 이력서 기반 질문 병합
```

#### WebSocket 엔드포인트 변경

```python
# Before
@router.websocket("/ws/interview/{interview_id}")
async def websocket_endpoint(websocket, interview_id):
    await interview_service_v4.handle_interview_session(websocket, interview_id)

# After
@router.websocket("/ws/interview/{interview_id}")
async def websocket_endpoint(websocket, interview_id, applicant_id=None):
    await interview_service_v4.handle_interview_session(websocket, interview_id, applicant_id)
```

### 17.2 아키텍처 결정

| 항목 | 결정 | 이유 |
|------|------|------|
| AWS Step Functions | 불필요 | LangGraph로 충분, 오버엔지니어링 방지 |
| 페르소나 하드코딩 | 의도적 | Mock 모드에서 테스트 용이성 |
| 3인 면접관 구조 | 채택 | 다각도 역량 평가 가능 |

### 17.3 테스트 방법

```bash
# 1. 서버 실행 (이미 실행 중)
cd /home/ec2-user/flex/server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 2. 프론트 실행 (이미 실행 중)
cd /home/ec2-user/flex/client
npm run dev

# 3. 브라우저에서 면접 시작
http://localhost:5173/interview
# → "면접 시작" 버튼 클릭
# → 김지원 이력서 기반 질문으로 3인 면접 진행
```

### 17.4 다음 작업 (채아 담당)

- [ ] 페르소나 + 질문 리스트 하드코딩 → AI 기반으로 변경
- [ ] 면접 종료 후 결과 처리 → 프론트 결과 페이지로 전달
- [ ] 이력서 업로드 → 질문 자동 생성 연동

---

**버전:** 1.4.0
**업데이트:** 2025-11-22 (작업 이력 추가)
