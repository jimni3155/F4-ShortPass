# Mock vs Real 경계 문서

> 시스템 전체의 Mock/Real 구현 현황 및 전환 가이드

---

## 1. 전체 현황 요약

| 모듈 | 현재 상태 | Mock 사용 이유 | Real 전환 필요 항목 |
|------|----------|---------------|-------------------|
| JD 업로드 | Mock | DB 충돌 회피 | SQLAlchemy Company 중복 해결 |
| 페르소나 생성 | Mock | LLM API 미설정 | OpenAI API 키 |
| 면접 진행 (STT/TTS) | Mock | AWS Polly 비용 | Polly 설정 |
| 평가 파이프라인 | Real | - | (완료) |
| 결과 조회 API | Mock | DB 연동 필요 | PostgreSQL 연동 |
| 프론트엔드 | Mock | API 미완성 | API 연동 |

---

## 2. 모듈별 상세

### 2.1 JD 업로드 (`/api/jd-persona/upload`)

**현재:** Mock
**파일:** `/server/api/jd_persona.py`

```python
# Mock 응답 (Line ~98-127)
mock_job_id = 1
common_competencies = [...]  # 하드코딩
job_competencies = [...]     # 하드코딩
```

**Real 전환 시:**
```python
# Real 구현 필요
1. PDF 파싱 (PyPDF2 or pdfplumber)
2. S3 업로드 (boto3)
3. LLM으로 역량 추출 (OpenAI)
4. DB 저장 (SQLAlchemy)
```

**의존성:**
- [ ] SQLAlchemy Company 모델 중복 해결
- [ ] S3 버킷 설정
- [ ] OpenAI API 키

---

### 2.2 페르소나 생성 (`/api/jd-persona/generate-persona`)

**현재:** Mock (persona_data.json 로드)
**파일:** `/server/api/jd_persona.py`, `/server/assets/persona_data.json`

```python
# Mock 응답 (Line ~158-217)
# persona_data.json에서 로드
PERSONA_JSON_PATH = Path(__file__).parent.parent / "assets" / "persona_data.json"
```

**Real 전환 시:**
```python
# Real 구현 필요
1. JD 텍스트 기반 역량 분석 (LLM)
2. 회사별 커스텀 가중치 계산
3. 페르소나 프로필 생성 (LLM)
4. DB 저장
```

**의존성:**
- [ ] OpenAI API 키
- [ ] 역량 추출 프롬프트 튜닝

---

### 2.3 면접 진행 (STT/TTS)

**현재:** Partial Mock
**파일:** `/server/services/interview_service_v4.py`

| 기능 | 상태 | 설명 |
|------|------|------|
| STT | Mock | 하드코딩된 transcript 사용 |
| TTS | Mock | AWS Polly 미연결 |
| 질문 생성 | Real | LLM 호출 (OpenAI) |

**Real 전환 시:**
- [ ] AWS Polly 설정 (TTS)
- [ ] AWS Transcribe 또는 Whisper (STT)
- [ ] WebSocket 실시간 스트리밍

---

### 2.4 평가 파이프라인

**현재:** Real
**파일:** `/server/services/evaluation_pipeline_service.py`

```python
# 실제 LLM 호출로 평가 수행
# 10개 역량 에이전트 + Aggregator
```

| 단계 | 상태 | 설명 |
|------|------|------|
| 1차 평가 (10 agents) | Real | LLM 병렬 호출 |
| Aggregator | Real | 결과 종합 |
| 후처리 | Real | 점수 정규화 |

**의존성:**
- [x] OpenAI API 키 (설정됨)
- [x] 프롬프트 파일들 (완료)

---

### 2.5 결과 조회 API

**현재:** Mock
**파일:** `/server/api/evaluation_db.py`

```python
# Mock 샘플 데이터 반환
# /server/test_data/evaluation_response_sample.json 참조
```

**Real 전환 시:**
```python
# Real 구현 필요
1. PostgreSQL evaluations 테이블 조회
2. S3에서 evidence 로드
3. 응답 포맷팅
```

**의존성:**
- [ ] PostgreSQL evaluations 테이블 생성
- [ ] S3 evidence 저장 로직

---

### 2.6 프론트엔드

**현재:** Mock
**파일:** `/client/src/pages/CandidateDetailPage.jsx`

```javascript
// Mock 데이터 사용
const mockDetailData = { ... };

useEffect(() => {
  setData(mockDetailData);  // Mock
  setLoading(false);
}, [applicantId]);
```

**Real 전환 시:**
```javascript
// API 호출로 변경
useEffect(() => {
  fetch(`/api/evaluation/${interviewId}`)
    .then(res => res.json())
    .then(data => setData(data));
}, [interviewId]);
```

---

## 3. 환경 변수 설정 현황

```bash
# 현재 설정됨
OPENAI_API_KEY=sk-proj-xxx  # 평가 파이프라인용

# 설정 필요 (Real 전환 시)
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_REGION=ap-northeast-2
S3_BUCKET_NAME=flex-interview-logs

DATABASE_URL=postgresql://user:pass@host:5432/flex
```

---

## 4. Mock → Real 전환 우선순위

### Phase 1: 핵심 기능 (높음)
1. **결과 조회 API** - DB 연동
2. **프론트엔드 API 연동** - fetch 호출

### Phase 2: 보조 기능 (중간)
3. **JD 업로드** - PDF 파싱 + S3
4. **페르소나 생성** - LLM 역량 분석

### Phase 3: 인터랙션 (낮음)
5. **STT/TTS** - AWS Polly/Transcribe

---

## 5. 테스트 데이터 파일

| 파일 | 용도 | Mock/Real |
|------|------|-----------|
| `test_data/transcript_official_sample.json` | 트랜스크립트 샘플 | Mock 입력 |
| `test_data/evaluation_response_sample.json` | 평가 결과 샘플 | Mock 출력 |
| `assets/persona_data.json` | 페르소나 정의 | Mock 설정 |

---

## 6. 팀별 담당

| 담당 | Mock 현황 확인 | Real 전환 |
|------|---------------|-----------|
| 지민 | 평가 파이프라인 | (완료) |
| 수민 | API 스펙 문서 | DB 연동 |
| 채아 | 프론트엔드 Mock | API 연동 |
| 지원 | 문서 정리 | - |

---

## 7. Quick Start: 현재 Mock 모드로 테스트

```bash
# 1. 서버 시작
cd /home/ec2-user/flex/server
source ../venv1/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# 2. 평가 테스트 (Real)
python tests/evaluation_test5.py

# 3. 프론트엔드 (Mock 데이터)
cd /home/ec2-user/flex/client
npm run dev
# http://localhost:5173/company/applicants/1/detail/101
```

---

*생성일: 2025-11-22*
*작성: 지원 (AI 시스템)*
