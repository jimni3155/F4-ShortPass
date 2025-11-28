# Evaluation JSON Schemas (Transcript, Multi-Agent, Persona/JD)

팀 합의용 JSON 포맷을 한 곳에 정리했습니다. 발표/Swagger/Mock 데이터에 동일하게 사용하세요.

샘플 파일 경로:
- Transcript 공식 샘플: `server/test_data/transcript_official_sample.json`
- Persona 샘플: `server/test_data/persona_samsung_fashion.json`
- 최종 응답 샘플(프론트/Swagger 용): `server/test_data/evaluation_response_sample.json`

## 1) Transcript 입력 (고정 JSON)
한 세그먼트 = 한 질문 + 한 답변. 페르소나/가중치를 함께 전달해 agent/aggregator가 동일한 컨텍스트를 사용.
```json
{
  "interview_id": 1,
  "applicant_id": 100,
  "job_id": 200,
  "persona_id": "P-001",
  "persona_meta": {
    "name": "Value-Driven PM",
    "role": "면접관",
    "tone": "차분/구조화",
    "focus": ["고객집착", "데이터기반"]
  },
  "weights": {
    "competency": {
      "COMM_01": 0.35, "COMM_02": 0.35, "COMM_03": 0.30,
      "JOB_01": 0.20, "JOB_02": 0.20, "JOB_03": 0.20, "JOB_04": 0.20, "JOB_05": 0.20
    },
    "category": { "common_competencies": 0.3, "job_competencies": 0.7 }
  },
  "segments": [
    {
      "segment_id": 1,
      "segment_order": 1,
      "turn_type": "main",       // main | follow_up
      "question_text": "질문",
      "answer_text": "답변",
      "answer_duration_sec": 60,
      "char_index_start": 0,
      "char_index_end": 280,
      "timestamp_start": "2025-11-22T04:00:00Z",
      "timestamp_end": "2025-11-22T04:01:00Z",
      "persona_hints": ["증거 요구", "ROI 근거 확인"] // 옵션
    }
  ]
}
```

필수: `interview_id`, `applicant_id`, `job_id`, `segments[].segment_id`, `segment_order`, `turn_type`, `question_text`, `answer_text`.

선택: `persona_id`, `persona_meta`, `weights`, `answer_duration_sec`, `char_index_*`, `timestamp_*`, `persona_hints`.

## 2) 멀티에이전트 평가 출력
에이전트/단계별 결과를 명확히 분리: `first_stage`(세그먼트 평가), `second_stage`(정규화/재평가), `aggregated`(최종 집계).
```json
{
  "interview_id": 1,
  "applicant_id": 100,
  "job_id": 200,
  "persona_id": "P-001",
  "weights": { ... }, // 입력 weights 그대로 재노출
  "first_stage": {
    "agent": "agent_v1",
    "segment_evaluations": [
      {
        "segment_id": 1,
        "competencies": [
          {
            "competency_id": "structured_thinking",
            "score": 86,
            "reason": "증거 기반 설명",
            "evidence": [{ "text": "...", "char_index": 120 }],
            "confidence": { "overall": 0.82, "evidence_strength": 0.8 }
          }
        ]
      }
    ]
  },
  "second_stage": {
    "agent": "cleanser_v1",
    "normalized": true,
    "notes": "키워드 매칭 금지, 의미 기반 점수 보정",
    "segment_summaries": [...]
  },
  "aggregated": {
    "job_aggregation": {
      "overall_job_score": 88.5,
      "structured_thinking": { "overall_score": 90, "confidence": { "overall_confidence": 0.82 } }
    },
    "common_aggregation": {
      "overall_common_score": 86.0,
      "problem_solving": { "overall_score": 87, "confidence": { "overall_confidence": 0.80 } }
    },
    "final_result": {
      "job_score": 88.5,
      "common_score": 86.0,
      "job_common_ratio": { "job": 0.6, "common": 0.4 },
      "final_score": 87.6,
      "confidence_overall": 0.81,
      "reliability_level": "high",
      "reliability_note": "증거 충분, 일관성 양호"
    }
  },
  "execution_logs": [
    {
      "phase": "first_stage",
      "node": "agent_v1",
      "duration_seconds": 2.1,
      "cost_usd": 0.003,
      "s3_key": "logs/evaluations/{applicant_id}/{interview_id}/20250101T000000Z_execution_logs.json"
    }
  ]
}
```

필드 규칙:
- `first_stage.segment_evaluations[].competencies[].confidence`: `overall`, `evidence_strength` 권장.
- `second_stage`는 재평가/정규화 로그용. 필요 시 `adjustments` 배열로 원점수/보정점수 기록.
- `aggregated.final_result`에 최종 점수, 가중치, 신뢰도(`confidence_overall` 또는 `reliability_level`) 포함.
- 실행 로그 S3 키는 `logs/evaluations/{applicant_id}/{interview_id}/{ts}_execution_logs.json` 고정.

## 3) Persona JSON (공통/직무 역량 공유)
```json
{
  "job_info": {
    "jd_id": "JD-001",
    "company_id": "COMP-001",
    "job_id": 200,
    "job_title": "Product Manager",
    "raw_text_s3": "s3://.../jd.pdf"
  },
  "persona_meta": {
    "persona_id": "P-001",
    "name": "Value-Driven PM",
    "role": "면접관",
    "tone": "차분하고 구조화된 질문",
    "goals": ["고객 집착 검증", "데이터 기반 사고 확인"]
  },
  "common_competencies": [
    { "id": "problem_solving", "display_name": "문제 해결", "weight": 0.25, "guide": "구조화/가설" },
    { "id": "organizational_fit", "display_name": "조직 적합도", "weight": 0.20, "guide": "가치 일치도" },
    { "id": "growth_potential", "display_name": "성장 잠재력", "weight": 0.20, "guide": "학습/실험" },
    { "id": "interpersonal_skills", "display_name": "커뮤니케이션", "weight": 0.20, "guide": "명확/협업" },
    { "id": "achievement_motivation", "display_name": "성과 지향", "weight": 0.15, "guide": "목표/실행" }
  ],
  "job_competencies": [
    { "id": "structured_thinking", "display_name": "구조적 사고", "weight": 0.25, "guide": "MECE/프레임워크" },
    { "id": "business_documentation", "display_name": "문서화", "weight": 0.20, "guide": "요약/스토리" },
    { "id": "financial_literacy", "display_name": "재무 감각", "weight": 0.20, "guide": "ROI/지표" },
    { "id": "industry_learning", "display_name": "도메인 학습", "weight": 0.20, "guide": "신규 산업 습득" },
    { "id": "stakeholder_management", "display_name": "이해관계자", "weight": 0.15, "guide": "조율/설득" }
  ],
  "question_guides": {
    "opening": ["자기소개", "핵심 경험"],
    "follow_up": ["증거 요청", "리스크 대응", "데이터 기반 설명"],
    "red_flag_checks": ["과장 여부", "모순 확인"]
  }
}
```

## 4) JD JSON (전처리 결과)
페르소나/에이전트/프론트가 공통 사용.
```json
{
  "jd_id": "JD-001",
  "company_id": "COMP-001",
  "job_id": 200,
  "company_name": "삼성물산",
  "job_title": "Product Manager",
  "raw_text": "...",
  "common_competencies": ["problem_solving", "organizational_fit", "growth_potential", "interpersonal_skills", "achievement_motivation"],
  "job_competencies": ["structured_thinking", "business_documentation", "financial_literacy", "industry_learning", "stakeholder_management"],
  "weights": {
    "common": { "problem_solving": 0.25, "organizational_fit": 0.20, "growth_potential": 0.20, "interpersonal_skills": 0.20, "achievement_motivation": 0.15 },
    "job": { "structured_thinking": 0.25, "business_documentation": 0.20, "financial_literacy": 0.20, "industry_learning": 0.20, "stakeholder_management": 0.15 }
  }
}
```

## 5) Resume 2단계 입력 (Transcript 이후 레이어, 옵션)
Transcript 1단계 평가 후 Resume를 보정 레이어로 쓸 때.
```json
{
  "resume_profile": {
    "raw_text": "...",
    "parsed": {
      "education": "OO대 OO과",
      "skills": ["Python", "SQL"],
      "experiences": [
        {
          "company": "ABC Corp",
          "role": "Data Analyst",
          "duration": "2022-2024",
          "highlights": ["ROI 150% 개선", "데이터 파이프라인 구축"]
        }
      ]
    }
  }
}
```

## 6) Mock vs Real (발표용 스코프 표시)
- **실제**: transcript 저장(JSON), 기본 점수 계산, 필터/정렬 UI, S3 로그 저장.
- **Mock**: 꼬리질문/엉뚱한 답변 감지 로직은 조건문+사전 답변, 동적 TTS/WS는 데모용 시나리오 스크립트.
- Swagger에는 실제 필드(`company_id`, `job_id`, `applicant_id`, `interview_id`, `persona_id`, 점수/가중치/신뢰도)를 명시하고, Mock-only 필드는 주석으로 구분.

## 7) 최종 UI/Swagger 응답 (후처리 포함)
- 목적: 지민 에이전트 결과 + 지원 후처리(긍/부 키워드, 추천질문, 전체 요약)를 합친 최종 응답 예시.
- 샘플: `server/test_data/evaluation_response_sample.json`
- 주요 필드:
  - 식별자: `interview_id`, `applicant_id`, `job_id`, `company_id`, `persona_id`
  - 점수: `scores.job_overall`, `scores.common_overall`, `scores.final_score`, `confidence_overall`, `reliability_level`, `job_common_ratio`
  - 역량 배열: `competencies[]` (id/name/category/score/confidence/strengths/weaknesses/evidence_segments)
  - 지민 요약: `analysis_summary.aggregator_summary` (심사평)
  - 지원 후처리: `analysis_summary.overall_applicant_summary`, `positive_keywords`, `negative_keywords`, `recommended_questions`
  - 증적/로그: `evidence.transcript_s3_key`, `execution_logs[]`
  - 후처리 메타: `post_processing.version`, `source`, `llm_used`
