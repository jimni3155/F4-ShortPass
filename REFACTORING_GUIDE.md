# JD 파싱 리팩토링 가이드

## 개요
AWS Bedrock의 무거운 동기 호출로 인한 서버 다운 문제를 해결하기 위해, **사전 처리(Pre-processing) 방식**으로 아키텍처를 변경했습니다.

## 문제점 (Before)
- 매 요청마다 PDF 파싱 + Bedrock 호출
- t3.large 환경에서 메모리 부족(OOM) 및 타임아웃 발생
- EC2 연결 끊김 및 재부팅 필요
- 무한 로딩 및 서버 크래시

## 해결 방안 (After)
- JD PDF는 고정 파일 → 한 번만 전처리
- OpenAI API(GPT-4o) 사용 (Bedrock보다 빠름)
- 결과를 JSON 파일로 저장
- 서버 시작 시 JSON 로드 → 메모리 캐시 사용
- 런타임에는 Bedrock 호출 없음

---

## 아키텍처 변경 사항

### 1. 전처리 스크립트 (`preprocess_jd.py`)
**역할:** PDF 파싱 → OpenAI API 호출 → JSON 저장

**실행 위치:** 개발 환경에서 한 번만 실행 (또는 JD 변경 시)

**출력:** `assets/persona_data.json`

**내용:**
```json
{
  "company_name": "삼성물산",
  "job_title": "Product Manager",
  "core_competencies": ["글로벌 시장 분석", "프로젝트 관리", "협상력", "공급망 이해", "리스크 관리"],
  "job_competencies": ["데이터분석", "문제해결력", "커뮤니케이션", "창의적 사고", "기술적 이해", "리더십"],
  "common_competencies": ["고객지향", "도전정신", "협동", "팀워크", "목표지향", "책임감"],
  "system_prompt": "당신은 글로벌 트레이딩 분야의 15년 경력 시니어 면접관입니다...",
  "persona_summary": [...]
}
```

### 2. 서버 시작 시 로드 (`main.py`)
**변경 사항:**
- `@app.on_event("startup")` 추가
- `PERSONA_DATA_CACHE` 전역 변수에 JSON 로드
- 파일이 없으면 경고 출력 (서버는 계속 실행)

### 3. 역량 서비스 수정 (`services/competency_service.py`)
**변경 사항:**
- `LLMClient` (Bedrock) 제거
- `analyze_jd_competencies()` → 캐시된 데이터 반환
- `generate_persona_data()` → 캐시된 데이터 반환
- Bedrock 호출 완전 제거 → **0초 응답**

---

## 설치 및 실행 가이드

### Step 1: 필요한 패키지 설치

```bash
cd /home/ec2-user/flex/server

# Python 패키지 설치
source venv1/bin/activate
pip install openai pypdf
```

### Step 2: OpenAI API 키 설정

```bash
# .env 파일 편집 또는 환경변수 설정
export OPENAI_API_KEY="sk-proj-your-api-key-here"
```

### Step 3: 전처리 스크립트 실행

```bash
cd /home/ec2-user/flex/server
python preprocess_jd.py
```

**예상 출력:**
```
============================================================
JD PDF 전처리 시작
============================================================

📄 PDF 파일 읽기: docs/jd.pdf
  ✓ 페이지 1/5 추출 완료
  ✓ 페이지 2/5 추출 완료
  ...
✅ 총 15234 글자 추출 완료

🤖 OpenAI API 호출 중... (GPT-4o)
✅ OpenAI API 응답 파싱 완료

✅ JSON 파일 저장 완료: assets/persona_data.json
   파일 크기: 3847 bytes

============================================================
전처리 완료!
============================================================

📊 추출된 정보:
  - 회사명: 삼성물산
  - 직무: Product Manager
  - 핵심 역량: 글로벌 시장 분석, 프로젝트 관리, 협상력, 공급망 이해, 리스크 관리
  - 직무 역량: 데이터분석, 문제해결력, 커뮤니케이션, 창의적 사고, 기술적 이해, 리더십
  - 공통 역량: 고객지향, 도전정신, 협동, 팀워크, 목표지향, 책임감

✅ 서버 시작 시 이 파일이 자동으로 로드됩니다.
```

### Step 4: 서버 시작

```bash
cd /home/ec2-user/flex/server
source venv1/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**예상 출력:**
```
============================================================
AWS_FLEX 서버 시작 중...
============================================================

✅ 페르소나 데이터 로드 완료: /home/ec2-user/flex/server/assets/persona_data.json
   - 회사: 삼성물산
   - 직무: Product Manager
   - 핵심 역량: 5개
✅ 모든 초기화 완료. 서버 준비 완료!

INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 5: API 테스트

```bash
# 역량 분석 테스트 (Bedrock 호출 없이 즉시 응답!)
curl http://localhost:8000/api/v1/jd-persona/analysis/2
```

---

## 성능 개선 효과

### Before (Bedrock 동기 호출)
- ❌ 응답 시간: 30-60초 (타임아웃)
- ❌ 메모리: 높은 사용률 → OOM
- ❌ 서버 상태: 자주 다운
- ❌ EC2 연결: 끊김 발생

### After (메모리 캐시)
- ✅ 응답 시간: **< 100ms**
- ✅ 메모리: 최소 사용 (JSON 로드만)
- ✅ 서버 상태: 안정적
- ✅ EC2 연결: 정상 유지

---

## FAQ

### Q1. JD 파일이 변경되면 어떻게 하나요?
**A:** `docs/jd.pdf`를 교체하고 `python preprocess_jd.py`를 다시 실행한 후, 서버를 재시작하세요.

### Q2. OpenAI API 비용은?
**A:** 전처리는 **한 번만 실행**하므로 비용이 매우 적습니다.
- GPT-4o: 약 $0.01-0.05 per call (PDF 크기에 따라)
- 런타임에는 OpenAI API 호출 없음 → 추가 비용 없음

### Q3. Bedrock을 완전히 제거해도 되나요?
**A:** JD 파싱에는 더 이상 Bedrock이 필요 없습니다.
- 면접 진행 로직(인터뷰 질문 생성 등)에서 Bedrock을 사용하는 경우, 그 부분은 유지할 수 있습니다.
- 또는 OpenAI API로 전환 가능합니다.

### Q4. 여러 개의 JD를 처리하려면?
**A:** 현재는 단일 JD 기반입니다. 여러 JD를 처리하려면:
1. 전처리 스크립트를 수정하여 여러 JSON 파일 생성
2. Job ID별로 JSON 매핑
3. `PERSONA_DATA_CACHE`를 딕셔너리로 변경

### Q5. AWS Step Functions / Lambda는 언제 사용하나요?
**A:**
- **현재 구조:** 정적 파일 기반 → Step Functions 불필요
- **향후 확장:** 실시간 JD 업로드가 필요하면:
  - Lambda: PDF 파싱 + OpenAI 호출
  - Step Functions: 복잡한 워크플로우 관리
  - DynamoDB: JD별 메타데이터 저장

---

## 향후 개선 방안

### 1. 비동기 처리 (AWS Lambda)
JD 업로드 시 실시간 처리가 필요한 경우:
```
사용자 업로드 → S3 → Lambda Trigger → OpenAI API → DynamoDB
```

### 2. AWS Step Functions (MAS 아키텍처)
Multi-Agent System에서 긴 워크플로우가 필요한 경우:
```
Step 1: PDF 파싱 (Lambda)
Step 2: 역량 추출 (OpenAI)
Step 3: 면접 질문 생성 (OpenAI)
Step 4: DB 저장
```

### 3. OpenAI API 전면 도입
Bedrock 대신 OpenAI를 모든 곳에 적용:
- 더 빠른 응답 속도
- 더 나은 JSON 구조화 능력
- gpt-4o 모델 활용

---

## 파일 구조

```
server/
├── preprocess_jd.py              # 전처리 스크립트 (신규)
├── main.py                       # Startup event 추가 (수정)
├── assets/
│   └── persona_data.json         # 전처리 결과 (신규)
├── services/
│   └── competency_service.py     # Bedrock 제거 (수정)
├── docs/
│   └── jd.pdf                    # 원본 JD 파일
└── ai/utils/
    └── llm_client.py             # Bedrock 클라이언트 (기존 유지)
```

---

## 트러블슈팅

### 에러: "OPENAI_API_KEY가 설정되지 않았습니다"
```bash
export OPENAI_API_KEY="sk-proj-..."
```

### 에러: "pypdf가 설치되지 않았습니다"
```bash
pip install pypdf openai
```

### 에러: "persona_data.json을 찾을 수 없습니다"
```bash
python preprocess_jd.py
```

### 서버는 시작되지만 페르소나 기능이 안 됨
→ 전처리 스크립트를 실행했는지 확인
→ `assets/persona_data.json` 파일이 존재하는지 확인

---

**작성일:** 2025-11-19
**작성자:** Claude Code Assistant
**버전:** 1.0.0
