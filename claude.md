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
