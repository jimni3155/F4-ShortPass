-- PostgreSQL Schema for Flex Interview System
-- This file is for reference only. Use init_db.py to create tables.

-- Enable pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- ==================== Company & Applicant Tables ====================

-- Companies table: 회사 정보
CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,

    -- 회사 정보
    company_values_text TEXT,
    company_culture_desc TEXT,

    -- 파싱 결과
    core_values JSONB,

    -- 가중치
    category_weights JSONB,  -- 4대 카테고리 가중치
    priority_weights JSONB,  -- 세부 우선순위 가중치

    -- 설정
    blind_mode BOOLEAN DEFAULT FALSE NOT NULL,

    -- 타임스탬프
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_companies_name ON companies(name);

-- Applicants table: 지원자 정보
CREATE TABLE IF NOT EXISTS applicants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(200) UNIQUE,

    -- 개인정보 (Blind 대상)
    age INTEGER,
    education VARCHAR(200),
    gender VARCHAR(20),

    -- 이력서/포트폴리오 파싱 결과
    skills JSONB,
    total_experience_years INTEGER DEFAULT 0,
    domain_experience JSONB,
    special_experience JSONB,

    -- 원본 파싱 데이터
    resume_parsed_data JSONB,
    portfolio_parsed_data JSONB,

    -- 파일 경로
    resume_file_path VARCHAR(500),
    portfolio_file_path VARCHAR(500),

    -- 타임스탬프
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_applicants_email ON applicants(email);

-- ==================== Job Tables ====================

-- Jobs table: 채용 공고 정보
CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_jobs_company_id ON jobs(company_id);

-- Job Chunks table: 채용 공고 청크 및 임베딩
CREATE TABLE IF NOT EXISTS job_chunks (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    embedding vector(1024),  -- Amazon Titan Text Embeddings V2 (1024 dimensions)
    chunk_index INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_job_chunks_job_id ON job_chunks(job_id);
CREATE INDEX IF NOT EXISTS ix_job_chunks_job_id_chunk_index ON job_chunks(job_id, chunk_index);

-- Vector similarity search index (HNSW)
-- m: max connections per layer (16 is good balance)
-- ef_construction: size of dynamic candidate list (64 is good for recall/speed tradeoff)
CREATE INDEX IF NOT EXISTS idx_job_chunks_embedding_hnsw
ON job_chunks
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Interview Sessions table: 면접 세션 정보
CREATE TYPE interview_status AS ENUM ('pending', 'in_progress', 'completed', 'failed');

CREATE TABLE IF NOT EXISTS interview_sessions (
    id SERIAL PRIMARY KEY,
    applicant_id INTEGER NOT NULL REFERENCES applicants(id),
    job_ids JSONB NOT NULL,  -- 1~3개 회사 지원 가능: [101, 102, 103]
    status interview_status DEFAULT 'pending' NOT NULL,
    current_question_index INTEGER DEFAULT 0 NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

ALTER TABLE interview_sessions 
ADD COLUMN evaluation_completed BOOLEAN DEFAULT FALSE NOT NULL;

CREATE INDEX IF NOT EXISTS ix_interview_sessions_applicant_id ON interview_sessions(applicant_id);

-- Interview Results table: 면접 질문별 답변 및 평가 결과
CREATE TABLE IF NOT EXISTS interview_results (
    id SERIAL PRIMARY KEY,
    interview_id INTEGER NOT NULL REFERENCES interview_sessions(id) ON DELETE CASCADE,
    question_id INTEGER,
    question_text TEXT,
    question_type VARCHAR(50),  -- technical, behavioral, situational, etc.

    -- 공통/기업별 구분
    is_common BOOLEAN DEFAULT FALSE NOT NULL,
    job_id INTEGER REFERENCES jobs(id),  -- 기업별 질문일 경우 해당 job_id (공통이면 NULL)

    -- STT 결과
    stt_full_text TEXT NOT NULL,  -- STT로 변환된 전체 답변 텍스트

    -- 평가 점수 (차원별 점수를 JSONB로 저장)
    scores JSONB,  -- {"python": 85, "system_design": 90, "collaboration": 88, ...}
    overall_score FLOAT,  -- 평균값 (정렬/인덱싱용)

    -- 분석 결과 (JSONB)
    keywords JSONB,  -- {"matched": ["Python", "FastAPI"], "missing": ["Docker"]}
    strengths JSONB,  -- ["strength1", "strength2", ...]
    weaknesses JSONB,  -- ["weakness1", "weakness2", ...]
    ai_feedback TEXT,
    metadata JSONB,  -- 추가 분석 데이터

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_interview_results_interview_id ON interview_results(interview_id);
CREATE INDEX IF NOT EXISTS ix_interview_results_question_id ON interview_results(question_id);
CREATE INDEX IF NOT EXISTS ix_interview_results_interview_question ON interview_results(interview_id, question_id);
CREATE INDEX IF NOT EXISTS ix_interview_results_overall_score ON interview_results(overall_score);
CREATE INDEX IF NOT EXISTS ix_interview_results_is_common ON interview_results(is_common);
CREATE INDEX IF NOT EXISTS ix_interview_results_job_id ON interview_results(job_id);

-- Questions table: 면접 질문 템플릿
CREATE TABLE IF NOT EXISTS questions (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id),
    question_type VARCHAR(50) NOT NULL,  -- technical, behavioral, situational, etc.
    question_text TEXT NOT NULL,
    expected_keywords JSONB,
    evaluation_criteria JSONB,
    difficulty_level INTEGER DEFAULT 3 NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_questions_job_id ON questions(job_id);
CREATE INDEX IF NOT EXISTS ix_questions_question_type ON questions(question_type);

ALTER TABLE questions 
ADD COLUMN evaluation_dimensions JSONB,
ADD COLUMN dimension_weights JSONB;

-- Example queries:

-- 1. Vector similarity search (find similar job descriptions)
/*
SELECT
    jc.job_id,
    jc.chunk_text,
    1 - (jc.embedding <=> '[0.1, 0.2, ...]'::vector) AS similarity
FROM job_chunks jc
ORDER BY jc.embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 10;
*/

-- 2. Get interview results with scores
/*
SELECT
    ir.interview_id,
    ir.question_text,
    ir.stt_full_text,
    ir.overall_score,
    ir.keywords,
    ir.strengths,
    ir.weaknesses
FROM interview_results ir
WHERE ir.interview_id = 1
ORDER BY ir.id;
*/

-- 3. Get top-performing interviews
/*
SELECT
    is_session.id,
    is_session.applicant_id,
    AVG(ir.overall_score) as avg_score,
    COUNT(ir.id) as answer_count
FROM interview_sessions is_session
JOIN interview_results ir ON ir.interview_id = is_session.id
WHERE is_session.status = 'completed'
GROUP BY is_session.id, is_session.applicant_id
ORDER BY avg_score DESC
LIMIT 20;
*/
