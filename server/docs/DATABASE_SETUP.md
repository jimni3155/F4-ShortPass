# Database Setup Guide
# @@ 클로드 
## 개요

이 프로젝트는 PostgreSQL과 pgvector를 사용하여 채용 공고 임베딩 및 면접 분석 결과를 저장합니다.

## 기술 스택

- **PostgreSQL**: 관계형 데이터베이스
- **pgvector**: 벡터 유사도 검색을 위한 PostgreSQL 확장
- **SQLAlchemy**: Python ORM
- **Alembic**: 데이터베이스 마이그레이션 도구

## 테이블 구조

### 1. Jobs 테이블
채용 공고 정보를 저장합니다.

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER | 기본 키 |
| company_id | INTEGER | 회사 ID |
| title | VARCHAR(500) | 채용 공고 제목 |
| description | TEXT | 채용 공고 전체 내용 |
| created_at | TIMESTAMP | 생성 시각 |
| updated_at | TIMESTAMP | 수정 시각 |

### 2. Job Chunks 테이블 ⭐
채용 공고를 청크 단위로 분할하여 벡터 임베딩과 함께 저장합니다.

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER | 기본 키 |
| job_id | INTEGER | 채용 공고 ID (FK) |
| chunk_text | TEXT | 청크 텍스트 |
| **embedding** | **vector(1024)** | **1024차원 벡터 임베딩** |
| chunk_index | INTEGER | 청크 순서 |
| created_at | TIMESTAMP | 생성 시각 |

**임베딩 모델**: Amazon Titan Text Embeddings V2 (1024 dimensions)

### 3. Interview Sessions 테이블
면접 세션 정보를 저장합니다.

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER | 기본 키 |
| applicant_id | INTEGER | 지원자 ID |
| job_id | INTEGER | 채용 공고 ID (FK) |
| status | ENUM | pending, in_progress, completed, failed |
| current_question_index | INTEGER | 현재 질문 인덱스 |
| started_at | TIMESTAMP | 면접 시작 시각 |
| completed_at | TIMESTAMP | 면접 완료 시각 |
| created_at | TIMESTAMP | 생성 시각 |

### 4. Interview Results 테이블 ⭐
면접 분석 결과를 저장합니다.

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER | 기본 키 |
| interview_id | INTEGER | 면접 세션 ID (FK) |
| question_id | INTEGER | 질문 ID |
| question_text | TEXT | 질문 내용 |
| **stt_full_text** | **TEXT** | **STT 변환된 답변 텍스트** |
| **logic_score** | **FLOAT** | **논리성 점수 (0-100)** |
| relevance_score | FLOAT | 적합성 점수 |
| technical_score | FLOAT | 기술 점수 |
| communication_score | FLOAT | 의사소통 점수 |
| overall_score | FLOAT | 종합 점수 |
| **keywords** | **JSONB** | **추출된 키워드** |
| strengths | JSONB | 강점 목록 |
| weaknesses | JSONB | 약점 목록 |
| ai_feedback | TEXT | AI 피드백 |
| metadata | JSONB | 추가 메타데이터 |
| created_at | TIMESTAMP | 생성 시각 |
| updated_at | TIMESTAMP | 수정 시각 |

**JSONB 예시**:
```json
{
  "keywords": {
    "technical": ["Python", "FastAPI", "PostgreSQL"],
    "soft_skills": ["communication", "teamwork"],
    "domain": ["machine learning", "data analysis"]
  },
  "strengths": [
    "Strong technical knowledge in backend development",
    "Good problem-solving approach"
  ],
  "weaknesses": [
    "Limited experience with distributed systems",
    "Could improve communication clarity"
  ]
}
```

### 5. Questions 테이블
면접 질문 템플릿을 저장합니다.

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER | 기본 키 |
| job_id | INTEGER | 채용 공고 ID (FK, nullable) |
| question_type | VARCHAR(50) | technical, behavioral, situational, etc. |
| question_text | TEXT | 질문 내용 |
| expected_keywords | JSONB | 기대되는 키워드 |
| evaluation_criteria | JSONB | 평가 기준 |
| difficulty_level | INTEGER | 난이도 (1-5) |
| created_at | TIMESTAMP | 생성 시각 |

## 설치 및 설정

### 1. 사전 요구사항

- PostgreSQL 14+ (pgvector 지원)
- Python 3.9+
- pip 또는 poetry

### 2. 패키지 설치

```bash
# 가상환경 활성화
source venv1/bin/activate

# 이미 설치됨:
# pip install sqlalchemy psycopg2-binary pgvector alembic
```

### 3. 환경 변수 설정

`.env` 파일을 생성하고 다음 내용을 추가합니다:

```bash
cp .env.example .env
nano .env
```

```bash
# .env
DATABASE_URL=postgresql://admin:password@your-rds-endpoint.us-east-1.rds.amazonaws.com:5432/flexdb
```

### 4. RDS PostgreSQL에서 pgvector 활성화

RDS 인스턴스에 연결 후:

```sql
-- pgvector 확장 활성화
CREATE EXTENSION IF NOT EXISTS vector;

-- 확인
\dx vector
```

### 5. 데이터베이스 초기화

```bash
cd /home/ec2-user/flex/server

# 데이터베이스 테이블 생성 및 pgvector 설정
python init_db.py
```

## 벡터 유사도 검색

### 인덱스 종류

프로젝트는 **HNSW (Hierarchical Navigable Small World)** 인덱스를 사용합니다:

```sql
CREATE INDEX idx_job_chunks_embedding_hnsw
ON job_chunks
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

**파라미터**:
- `m = 16`: 각 레이어의 최대 연결 수 (높을수록 정확도 증가, 인덱스 크기 증가)
- `ef_construction = 64`: 인덱스 구축 시 동적 후보 목록 크기 (높을수록 정확도 증가, 구축 시간 증가)

### 유사도 검색 쿼리 예시

#### Python (SQLAlchemy)
```python
from pgvector.sqlalchemy import cosine_distance
from models import JobChunk
from db import SessionLocal

# 쿼리 임베딩 (Amazon Titan으로 생성)
query_embedding = [0.1, 0.2, 0.3, ...]  # 1024 dimensions

db = SessionLocal()

# 코사인 유사도로 Top 5 검색
results = db.query(
    JobChunk.id,
    JobChunk.chunk_text,
    JobChunk.job_id
).order_by(
    cosine_distance(JobChunk.embedding, query_embedding)
).limit(5).all()

for result in results:
    print(f"Job ID: {result.job_id}")
    print(f"Text: {result.chunk_text}\n")
```

#### Raw SQL
```sql
-- 코사인 유사도 검색 (1 - cosine_distance)
SELECT
    jc.id,
    jc.job_id,
    jc.chunk_text,
    1 - (jc.embedding <=> '[0.1, 0.2, ...]'::vector) AS similarity
FROM job_chunks jc
ORDER BY jc.embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 10;
```

**거리 연산자**:
- `<=>`: 코사인 거리 (cosine distance)
- `<->`: L2 거리 (Euclidean distance)
- `<#>`: 내적 거리 (negative inner product)

## 사용 예시

### 1. Job Chunk 저장

```python
from models import Job, JobChunk
from db import SessionLocal
import numpy as np

db = SessionLocal()

# 1. Job 생성
job = Job(
    company_id=1,
    title="Backend Engineer",
    description="Full job description..."
)
db.add(job)
db.commit()

# 2. Job Chunk 생성 및 임베딩 저장
chunk_text = "We are looking for a backend engineer with Python experience..."
embedding = generate_embedding(chunk_text)  # [1024 dimensions]

job_chunk = JobChunk(
    job_id=job.id,
    chunk_text=chunk_text,
    embedding=embedding,
    chunk_index=0
)
db.add(job_chunk)
db.commit()
```

### 2. Interview Result 저장

```python
from models import InterviewSession, InterviewResult, InterviewStatus
from db import SessionLocal

db = SessionLocal()

# 1. Interview Session 생성
session = InterviewSession(
    applicant_id=123,
    job_id=1,
    status=InterviewStatus.IN_PROGRESS
)
db.add(session)
db.commit()

# 2. Interview Result 저장
result = InterviewResult(
    interview_id=session.id,
    question_id=1,
    question_text="Tell me about your experience with Python",
    stt_full_text="I have been working with Python for 5 years...",
    logic_score=85.5,
    relevance_score=90.0,
    technical_score=88.0,
    communication_score=82.0,
    overall_score=86.375,
    keywords={
        "technical": ["Python", "Django", "REST API"],
        "soft_skills": ["teamwork", "communication"],
        "domain": ["web development", "microservices"]
    },
    strengths=[
        "Strong Python expertise",
        "Good understanding of microservices architecture"
    ],
    weaknesses=[
        "Limited experience with async programming",
        "Could provide more specific examples"
    ],
    ai_feedback="The candidate demonstrated solid technical knowledge..."
)
db.add(result)
db.commit()
```

### 3. Interview Results 조회

```python
from models import InterviewResult
from db import SessionLocal

db = SessionLocal()

# 특정 면접의 모든 결과 조회
results = db.query(InterviewResult).filter(
    InterviewResult.interview_id == 1
).all()

for result in results:
    print(f"Question: {result.question_text}")
    print(f"Answer: {result.stt_full_text}")
    print(f"Overall Score: {result.overall_score}")
    print(f"Keywords: {result.keywords}")
    print(f"Strengths: {result.strengths}")
    print(f"Weaknesses: {result.weaknesses}\n")
```

## 마이그레이션 (향후)

Alembic을 사용한 스키마 마이그레이션:

```bash
# 초기화
alembic init alembic

# 마이그레이션 생성
alembic revision --autogenerate -m "Add new column"

# 마이그레이션 적용
alembic upgrade head
```

## 참고 자료

- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Amazon Titan Embeddings](https://aws.amazon.com/bedrock/titan/)
- [HNSW Algorithm](https://arxiv.org/abs/1603.09320)

## 문제 해결

### pgvector 확장이 활성화되지 않는 경우

```sql
-- 수동으로 활성화
CREATE EXTENSION IF NOT EXISTS vector;

-- RDS의 경우 파라미터 그룹에서 shared_preload_libraries 확인
```

### 벡터 인덱스 생성 실패

```bash
# 테이블에 데이터가 없거나 적으면 인덱스 생성이 실패할 수 있습니다
# 데이터를 먼저 삽입한 후 인덱스 생성
```

### 연결 풀 고갈

```bash
# .env에서 풀 크기 조정
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
```
