-- 004_add_rag_fields_to_jobs.sql
-- RAG Agent 파싱 결과를 저장할 필드 추가

-- Jobs 테이블에 RAG Agent 관련 필드 추가
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS required_skills JSONB;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS preferred_skills JSONB;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS domain_requirements JSONB;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS dynamic_evaluation_criteria JSONB;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS seniority_level VARCHAR(50);
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS main_responsibilities JSONB;

-- 기존 competency_weights, position_type 컬럼이 없으면 추가 (이미 있을 수 있음)
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS competency_weights JSONB;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS position_type VARCHAR(100);

-- 인덱스 추가 (position_type, seniority_level로 필터링 가능)
CREATE INDEX IF NOT EXISTS idx_jobs_position_type ON jobs(position_type);
CREATE INDEX IF NOT EXISTS idx_jobs_seniority_level ON jobs(seniority_level);

-- 코멘트 추가
COMMENT ON COLUMN jobs.required_skills IS 'JD에서 추출한 필수 기술 리스트 (RAG Agent)';
COMMENT ON COLUMN jobs.preferred_skills IS 'JD에서 추출한 우대 기술 리스트 (RAG Agent)';
COMMENT ON COLUMN jobs.domain_requirements IS 'JD에서 추출한 도메인 요구사항 (RAG Agent)';
COMMENT ON COLUMN jobs.dynamic_evaluation_criteria IS '동적 평가 기준 5개 (RAG Agent)';
COMMENT ON COLUMN jobs.competency_weights IS '역량별 가중치 (job_expertise, analytical 등)';
COMMENT ON COLUMN jobs.position_type IS '포지션 타입 (backend, frontend, fullstack 등)';
COMMENT ON COLUMN jobs.seniority_level IS '시니어리티 레벨 (junior, mid, senior, lead 등)';
COMMENT ON COLUMN jobs.main_responsibilities IS '주요 업무 리스트';
