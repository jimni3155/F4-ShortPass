# FLEX (SHORT-PASS) 프로젝트

AI 기반 면접 및 채용 매칭 서비스. 기업 채용담당자가 AI 면접관을 통해 지원자를 평가하고 직무 매칭 정도를 자동 분석하는 HR 스크리닝 플랫폼.

## 기술 스택

### Frontend (client/)
- React 19 + Vite
- Tailwind CSS
- Recharts (차트)
- React Router v7

### Backend (server/)
- FastAPI + Uvicorn
- SQLAlchemy + PostgreSQL (RDS)
- LangGraph (멀티에이전트 워크플로우)
- OpenAI GPT-4o
- pgvector (임베딩)
- AWS S3, Polly, Bedrock

## 디렉토리 구조

```
flex/
├── client/                     # 프론트엔드
│   └── src/
│       ├── pages/              # 페이지 컴포넌트
│       ├── components/         # 재사용 UI
│       ├── lib/                # 유틸리티 (apiConfig, hooks)
│       └── App.jsx             # 라우팅
│
└── server/                     # 백엔드
    ├── ai/
    │   ├── agents/             # 평가 에이전트
    │   │   ├── competency_agent.py
    │   │   └── graph/          # LangGraph 워크플로우
    │   └── prompts/            # 역량별 프롬프트
    ├── api/                    # REST API
    ├── models/                 # SQLAlchemy 모델
    ├── services/               # 비즈니스 로직
    └── main.py
```

## 핵심 기능

### 1. MAS (멀티에이전트 시스템) 평가 파이프라인
```
Stage 1: 10개 CompetencyAgent 병렬 평가
    ↓
Stage 2: Resume 검증 + 신뢰도 계산 + 중복 조정
    ↓
Stage 3: 최종 점수 통합
    ↓
Stage 4: 프론트엔드 포맷 생성
```

### 2. 평가 역량 (10개)
- **공통 (5개)**: 문제해결력, 조직적응력, 성장잠재력, 대인관계, 성취동기
- **직무 (5개)**: 고객여정마케팅, 데이터분석, 시즌전략KPI, 이해관계자협업, 가치사슬최적화

## 주요 API 엔드포인트

### 면접
```
POST /api/v1/interviews/prepare     # 면접 세션 준비
WS   /api/v1/interviews/ws/{id}     # 실시간 면접 (WebSocket)
```

### 평가
```
POST /api/v1/evaluations/           # 평가 실행
GET  /api/v1/evaluations/{id}       # 평가 결과 조회
```

### Agent Logs (MAS 분석용)
```
GET  /api/v1/agent-logs/list/recent              # 최근 평가 목록
GET  /api/v1/agent-logs/{evaluation_id}          # 전체 에이전트 로그
GET  /api/v1/agent-logs/{evaluation_id}/stage/1  # 특정 Stage 로그
GET  /api/v1/agent-logs/{evaluation_id}/competency/{name}  # 역량별 상세
```

## 주요 페이지 (Frontend)

| 경로 | 페이지 | 설명 |
|------|--------|------|
| `/` | Start | 홈 (기업/지원자 선택) |
| `/candidate/info` | CandidateInfo | 지원자 정보 입력 |
| `/candidate/interview` | InterviewPage | AI 면접 진행 |
| `/company/info` | PersonaGeneration | JD 분석 및 페르소나 설정 |
| `/company/result` | InterviewResult | 면접 결과 목록 |
| `/company/applicant/:id` | CandidateEvaluation | 지원자 상세 평가 |
| `/agent-logs` | AgentLogs | MAS 에이전트 로그 분석 |
| `/agent-logs/:evaluationId` | AgentLogs | 특정 평가 상세 |

## S3 저장 구조

평가 완료 시 S3에 상세 로그 저장:
```
s3://linkbig-ht-06-f4/evaluations/{interview_id}/{timestamp}/
├── stage1_evidence.json              # 역량별 평가 결과
├── stage2_aggregator.json            # 통합/검증 결과
├── stage3_final_integration.json     # 최종 결과
└── stage4_presentation_frontend.json # 프론트엔드 포맷
```

## 개발 서버 실행

```bash
# 백엔드
cd server
source ../venv1/bin/activate
uvicorn main:app --reload --port 8000

# 프론트엔드
cd client
npm run dev
```

## 환경 변수 (.env)

```
DATABASE_URL=postgresql://...
OPENAI_API_KEY=sk-...
AWS_REGION=us-east-1
S3_BUCKET_NAME=linkbig-ht-06-f4
```

## 최근 작업 이력

### 2024-11-24: Agent Logs 페이지 추가
- **API**: `server/api/agent_logs.py`
  - S3에 저장된 MAS 평가 과정 조회
  - Stage별, 역량별 상세 로그 제공
- **Frontend**: `client/src/pages/AgentLogs.jsx`
  - 에이전트 아키텍처 다이어그램 시각화
  - Stage 1~4 파이프라인 뷰
  - 역량별 상세 패널 (강점/약점/세그먼트)
