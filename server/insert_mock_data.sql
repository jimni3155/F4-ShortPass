-- Mock 데이터 삽입 (삼성물산 패션부문)

-- 1. Company 데이터
INSERT INTO companies (id, name, size, values, blind, jd)
VALUES (
    1,
    '삼성물산 패션부문',
    '대기업',
    '혁신, 도전, 글로벌',
    false,
    '{"roles": ["상품기획(MD/MR)", "Retail영업"], "description": "국내/글로벌 브랜드의 전략과 상품 컨셉을 기획하고 생산, 마케팅, 판매까지의 전 과정을 관리"}'::jsonb
)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    size = EXCLUDED.size,
    values = EXCLUDED.values;

-- 2. Job 데이터
INSERT INTO jobs (id, company_id, title, description, dynamic_evaluation_criteria, position_type, seniority_level)
VALUES (
    1,
    1,
    '상품기획(MD/MR) / Retail영업',
    '국내/글로벌 브랜드의 전략과 상품 컨셉을 기획하고 생산, 마케팅, 판매까지의 전 과정을 관리하거나, 온/오프라인 채널의 매출 목표를 달성하기 위한 영업 전략을 수립하는 직무',
    '["Market & Trend Insight", "Strategic Thinking", "Creativity & Execution", "Communication", "Global & Business Mindset"]'::jsonb,
    'MD/MR',
    'Junior-Senior'
)
ON CONFLICT (id) DO UPDATE SET
    title = EXCLUDED.title,
    description = EXCLUDED.description,
    dynamic_evaluation_criteria = EXCLUDED.dynamic_evaluation_criteria;

-- 3. JDPersona 데이터
INSERT INTO jd_personas (
    id, job_id, company_id, company_name,
    common_competencies, job_competencies, core_questions,
    persona_summary, analysis_summary, is_active
)
VALUES (
    1,
    1,
    1,
    '삼성물산 패션부문',
    '["고객지향", "도전정신", "협동", "목표지향", "책임감"]'::jsonb,
    '["Market & Trend Insight", "Strategic Thinking", "Creativity & Execution", "Communication", "Global & Business Mindset"]'::jsonb,
    '[
        "삼성물산 패션부문에 지원해주셔서 감사합니다. 최근 가장 인상 깊게 본 패션 트렌드는 무엇이며, 그것을 우리 브랜드의 시즌 전략에 어떻게 적용할 수 있을지 말씀해 주시겠습니까?",
        "패션 상품기획(또는 영업) 직무는 유관부서와의 협업이 필수적입니다. 의견 차이가 발생했을 때 데이터나 논리를 활용해 상대를 설득했던 구체적인 경험이 있나요?",
        "만약 담당하고 있는 브랜드의 특정 시즌 매출이 목표 대비 30% 미달하고 있다면, 어떤 데이터를 먼저 분석하고 어떻게 대응 전략을 수립하시겠습니까?"
    ]'::jsonb,
    '[
        {
            "type": "전략적 사고형 면접관",
            "focus": "시장 분석 및 데이터 기반 의사결정 능력 평가",
            "style": "논리적이고 분석적, 구체적인 근거를 요구",
            "target_competencies": ["Market & Trend Insight", "Strategic Thinking"]
        },
        {
            "type": "실행력 중심형 면접관",
            "focus": "목표 달성을 위한 창의적 실행과 협업 능력 평가",
            "style": "실무 경험과 구체적 성과를 중시",
            "target_competencies": ["Creativity & Execution", "Communication"]
        },
        {
            "type": "글로벌 비즈니스형 면접관",
            "focus": "글로벌 감각과 비즈니스 마인드 평가",
            "style": "전략적 사고와 글로벌 시각을 평가",
            "target_competencies": ["Global & Business Mindset"]
        }
    ]'::jsonb,
    '삼성물산 패션부문 MD/영업 직무에 필요한 핵심 역량 5개 분석 완료',
    true
)
ON CONFLICT (id) DO UPDATE SET
    common_competencies = EXCLUDED.common_competencies,
    job_competencies = EXCLUDED.job_competencies,
    core_questions = EXCLUDED.core_questions,
    persona_summary = EXCLUDED.persona_summary;

-- 4. PersonaInstance 데이터 (3명의 면접관)
INSERT INTO persona_instances (id, company_id, instance_name, system_prompt, focus_area, question_style, target_competencies, is_active)
VALUES
    (
        1,
        1,
        '전략적 사고형 면접관',
        '당신은 삼성물산 패션부문의 15년 차 시니어 채용 담당자이자 면접관입니다. 당신은 지원자가 ''패션산업 및 소비재 트렌드에 대한 폭넓은 이해''와 ''논리적인 전략적 사고력''을 갖추었는지 검증해야 합니다. 단순히 지식을 묻기보다는, 실제 비즈니스 상황(매출 부진, 트렌드 변화 등)에서 어떻게 문제를 해결할 것인지 구체적인 경험과 로직을 묻는 ''구조화 면접''을 진행하세요. 말투는 전문적이고 정중하지만, 지원자의 답변이 추상적일 경우 집요하게 구체적인 근거를 요구하는 압박 면접 스타일을 일부 혼합하세요. 한 번에 하나의 질문만 하세요.',
        '시장 분석 및 데이터 기반 의사결정 능력 평가',
        '논리적이고 분석적, 구체적인 근거를 요구',
        '["Market & Trend Insight", "Strategic Thinking"]'::jsonb,
        true
    ),
    (
        2,
        1,
        '실행력 중심형 면접관',
        '당신은 삼성물산 패션부문의 15년 차 시니어 채용 담당자이자 면접관입니다. 당신은 지원자가 ''패션산업 및 소비재 트렌드에 대한 폭넓은 이해''와 ''논리적인 전략적 사고력''을 갖추었는지 검증해야 합니다. 단순히 지식을 묻기보다는, 실제 비즈니스 상황(매출 부진, 트렌드 변화 등)에서 어떻게 문제를 해결할 것인지 구체적인 경험과 로직을 묻는 ''구조화 면접''을 진행하세요. 말투는 전문적이고 정중하지만, 지원자의 답변이 추상적일 경우 집요하게 구체적인 근거를 요구하는 압박 면접 스타일을 일부 혼합하세요. 한 번에 하나의 질문만 하세요.',
        '목표 달성을 위한 창의적 실행과 협업 능력 평가',
        '실무 경험과 구체적 성과를 중시',
        '["Creativity & Execution", "Communication"]'::jsonb,
        true
    ),
    (
        3,
        1,
        '글로벌 비즈니스형 면접관',
        '당신은 삼성물산 패션부문의 15년 차 시니어 채용 담당자이자 면접관입니다. 당신은 지원자가 ''패션산업 및 소비재 트렌드에 대한 폭넓은 이해''와 ''논리적인 전략적 사고력''을 갖추었는지 검증해야 합니다. 단순히 지식을 묻기보다는, 실제 비즈니스 상황(매출 부진, 트렌드 변화 등)에서 어떻게 문제를 해결할 것인지 구체적인 경험과 로직을 묻는 ''구조화 면접''을 진행하세요. 말투는 전문적이고 정중하지만, 지원자의 답변이 추상적일 경우 집요하게 구체적인 근거를 요구하는 압박 면접 스타일을 일부 혼합하세요. 한 번에 하나의 질문만 하세요.',
        '글로벌 감각과 비즈니스 마인드 평가',
        '전략적 사고와 글로벌 시각을 평가',
        '["Global & Business Mindset"]'::jsonb,
        true
    )
ON CONFLICT (id) DO UPDATE SET
    instance_name = EXCLUDED.instance_name,
    system_prompt = EXCLUDED.system_prompt,
    focus_area = EXCLUDED.focus_area,
    question_style = EXCLUDED.question_style,
    target_competencies = EXCLUDED.target_competencies;

-- 결과 확인
SELECT '✅ Mock 데이터 삽입 완료!' AS status;
SELECT 'Company ID: ' || id || ' - ' || name FROM companies WHERE id = 1;
SELECT 'Job ID: ' || id || ' - ' || title FROM jobs WHERE id = 1;
SELECT 'JDPersona ID: ' || id || ' (역량 ' || jsonb_array_length(job_competencies) || '개)' FROM jd_personas WHERE id = 1;
SELECT 'PersonaInstance: ' || COUNT(*) || '명' FROM persona_instances WHERE company_id = 1;
