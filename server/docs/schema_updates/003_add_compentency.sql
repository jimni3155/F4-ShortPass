-- ==================== Evaluation System Tables ====================
-- 새로운 6-competency 평가 시스템을 위한 테이블
-- Phase 2: Multiagent Evaluation System

-- Competency Evaluations table: 각 역량별 평가 결과 저장
CREATE TABLE IF NOT EXISTS competency_evaluations (
    id SERIAL PRIMARY KEY,
    interview_id INTEGER NOT NULL REFERENCES interview_sessions(id) ON DELETE CASCADE,
    job_id INTEGER NOT NULL REFERENCES jobs(id),
    
    -- 평가 메타데이터
    evaluation_status VARCHAR(50) DEFAULT 'pending' NOT NULL,  
    -- 'pending', 'evaluating', 'adversarial_validation', 'completed', 'failed'
    
    -- 6개 역량별 평가 결과 (JSONB)
    job_expertise JSONB,  -- {score, raw_score, reasoning, evidence, flags, sub_scores}
    problem_solving JSONB,
    organizational_fit JSONB,
    growth_potential JSONB,
    interpersonal_skill JSONB,
    achievement_motivation JSONB,
    overall_feedback TEXT,
    key_insights JSONB,

    -- 통합 점수 (Aggregator 결과)
    weighted_total_score FLOAT,  -- 가중치 적용된 총점
    raw_total_score FLOAT,  -- 가중치 미적용 총점
    aggregation_reasoning TEXT,  -- Aggregator의 종합 판단
    
    hiring_recommendation VARCHAR(50),  -- 'strong_hire', 'hire', 'hold', 'no_hire'
    recommendation_reasoning TEXT,
    
    -- Position Level 제거하고 Job Fit으로 대체
    job_requirement_fit_score FLOAT,  -- 0-100: 해당 포지션 요구사항 충족도
    fit_analysis TEXT,  -- "신입 백엔드 개발자 요구사항 대비 85% 충족. Python/FastAPI는 우수하나 Docker 경험 부족..."
    
    -- 온보딩 예측
    expected_onboarding_duration VARCHAR(50),  -- 'immediate', '1-3months', '3-6months'
    onboarding_support_needed JSONB,  -- ["Docker 교육", "아키텍처 리뷰 참여"]
   
    -- 타임스탬프
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    UNIQUE(interview_id, job_id)  -- 한 인터뷰-잡 조합당 하나의 평가
);

CREATE INDEX IF NOT EXISTS ix_competency_evaluations_interview_id 
    ON competency_evaluations(interview_id);
CREATE INDEX IF NOT EXISTS ix_competency_evaluations_job_id 
    ON competency_evaluations(job_id);
CREATE INDEX IF NOT EXISTS ix_competency_evaluations_status 
    ON competency_evaluations(evaluation_status);
CREATE INDEX IF NOT EXISTS ix_competency_evaluations_weighted_score 
    ON competency_evaluations(weighted_total_score);


-- Adversarial Challenges table: Adversarial Validation 결과 저장
CREATE TABLE IF NOT EXISTS adversarial_challenges (
    id SERIAL PRIMARY KEY,
    competency_evaluation_id INTEGER NOT NULL REFERENCES competency_evaluations(id) ON DELETE CASCADE,
    
    -- Challenge 대상
    competency_name VARCHAR(50) NOT NULL,  -- 'job_expertise', 'problem_solving', etc.
    original_score FLOAT NOT NULL,
    
    -- Challenge 내용
    challenge_text TEXT NOT NULL,
    challenge_severity VARCHAR(20) NOT NULL,  -- 'low', 'medium', 'high'
    suggested_score_adjustment INTEGER,  -- -10 ~ +10
    challenge_reasoning TEXT,
    
    -- Refiner 응답
    refiner_decision VARCHAR(20),  -- 'accept', 'reject', 'partial_accept'
    final_score FLOAT,
    refiner_reasoning TEXT,
    
    -- 타임스탬프
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_adversarial_challenges_evaluation_id 
    ON adversarial_challenges(competency_evaluation_id);
CREATE INDEX IF NOT EXISTS ix_adversarial_challenges_competency_name 
    ON adversarial_challenges(competency_name);


-- Evaluation Logs table: 평가 과정 전체 로그 (디버깅/투명성)
CREATE TABLE IF NOT EXISTS evaluation_logs (
    id SERIAL PRIMARY KEY,
    competency_evaluation_id INTEGER NOT NULL REFERENCES competency_evaluations(id) ON DELETE CASCADE,
    
    -- 로그 메타
    log_type VARCHAR(50) NOT NULL,  -- 'evaluator', 'aggregator', 'adversarial', 'refiner'
    agent_name VARCHAR(100),  -- 'job_expertise_evaluator', 'adversarial_validator', etc.
    
    -- 로그 내용
    input_data JSONB,  -- 해당 agent에 전달된 입력
    output_data JSONB,  -- agent가 반환한 출력
    prompt_used TEXT,  -- 실제 사용된 프롬프트 (디버깅용)
    
    -- 성능 메트릭
    execution_time_ms INTEGER,  -- 실행 시간 (밀리초)
    token_count INTEGER,  -- 사용된 토큰 수
    
    -- 에러 처리
    error_occurred BOOLEAN DEFAULT FALSE,
    error_message TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_evaluation_logs_evaluation_id 
    ON evaluation_logs(competency_evaluation_id);
CREATE INDEX IF NOT EXISTS ix_evaluation_logs_log_type 
    ON evaluation_logs(log_type);
CREATE INDEX IF NOT EXISTS ix_evaluation_logs_agent_name 
    ON evaluation_logs(agent_name);


-- ==================== Jobs 테이블 확장 ====================
-- 기존 jobs 테이블에 컬럼 추가

ALTER TABLE jobs 
ADD COLUMN IF NOT EXISTS extracted_skills JSONB,  -- ['Python', 'FastAPI', 'PostgreSQL', ...]
ADD COLUMN IF NOT EXISTS jd_full_text TEXT,  -- PDF에서 추출한 전체 텍스트
ADD COLUMN IF NOT EXISTS competency_weights JSONB,  -- {job_expertise: 0.3, problem_solving: 0.2, ...}
ADD COLUMN IF NOT EXISTS weights_reasoning TEXT;  -- 가중치 산정 근거
