const candidateListMock = {
  "company_name": "삼성물산 패션부문",
  "job_title": "상품기획(MD) / Retail영업",
  "total_applicants": 5,
  "completed_evaluations": 5,
  "average_score": 75.4,
  "applicants": [
    {
      "applicant_id": "CAND_001",
      "job_id": "JOB_001",
      "rank": 1,
      "applicant_name": "김지원",
      "track": "상품기획(MD)",
      "total_score": 92,
      "strengths": "Data-Driven Insight",
      "weaknesses": "Global Mindset",
      "ai_summary_comment": "데이터 기반 가설 검증 능력이 탁월하며, 논리적 구조화가 매우 뛰어남.",
      "status": "추천",
      "competency_scores": [
        { "name": "Data Insight", "score": 95 },
        { "name": "Strategic Solving", "score": 90 },
        { "name": "Value Chain", "score": 85 },
        { "name": "Marketing", "score": 88 },
        { "name": "Stakeholder", "score": 80 }
      ]
    },
    {
      "applicant_id": "CAND_002",
      "job_id": "JOB_001",
      "rank": 2,
      "applicant_name": "이삼성",
      "track": "Retail영업",
      "total_score": 88,
      "strengths": "Stakeholder Mgmt",
      "weaknesses": "Creativity & Execution",
      "ai_summary_comment": "유관부서 설득 논리가 명확하나, 위기 상황 대처의 구체성이 다소 부족함.",
      "status": "추천",
      "competency_scores": [
        { "name": "Data Insight", "score": 82 },
        { "name": "Strategic Solving", "score": 85 },
        { "name": "Value Chain", "score": 80 },
        { "name": "Marketing", "score": 90 },
        { "name": "Stakeholder", "score": 92 }
      ]
    },
    {
      "applicant_id": "CAND_003",
      "job_id": "JOB_001",
      "rank": 3,
      "applicant_name": "박물산",
      "track": "상품기획(MD)",
      "total_score": 74,
      "strengths": "Value Chain Optimization",
      "weaknesses": "Strategic Problem Solving",
      "ai_summary_comment": "실무 경험은 풍부하나, 전략적 의사결정의 근거가 직관에 의존함.",
      "status": "보류",
      "competency_scores": [
        { "name": "Data Insight", "score": 70 },
        { "name": "Strategic Solving", "score": 65 },
        { "name": "Value Chain", "score": 88 },
        { "name": "Marketing", "score": 72 },
        { "name": "Stakeholder", "score": 75 }
      ]
    },
    {
      "applicant_id": "CAND_004",
      "job_id": "JOB_001",
      "rank": 4,
      "applicant_name": "최혁신",
      "track": "Retail영업",
      "total_score": 65,
      "strengths": "Customer Journey & Marketing Strategy",
      "weaknesses": "Data-Driven Insight",
      "ai_summary_comment": "마케팅 전략 수립에 강점이나, 데이터 분석 능력 향상 필요.",
      "status": "검토 필요",
      "competency_scores": [
        { "name": "Data Insight", "score": 55 },
        { "name": "Strategic Solving", "score": 60 },
        { "name": "Value Chain", "score": 68 },
        { "name": "Marketing", "score": 78 },
        { "name": "Stakeholder", "score": 65 }
      ]
    },
    {
      "applicant_id": "CAND_005",
      "job_id": "JOB_001",
      "rank": 5,
      "applicant_name": "정열정",
      "track": "상품기획(MD)",
      "total_score": 58,
      "strengths": "Creativity & Execution",
      "weaknesses": "All competencies need improvement",
      "ai_summary_comment": "열정적이나, 직무 관련 핵심 역량 전반에 걸쳐 보완이 필요함.",
      "status": "미흡",
      "competency_scores": [
        { "name": "Data Insight", "score": 50 },
        { "name": "Strategic Solving", "score": 55 },
        { "name": "Value Chain", "score": 60 },
        { "name": "Marketing", "score": 62 },
        { "name": "Stakeholder", "score": 58 }
      ]
    }
  ]
};

export default candidateListMock;
