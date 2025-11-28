const candidateDetailMock = {
  interview_id: 90001,
  applicant_id: 101,
  applicant_name: "김지원",
  job_id: 1,
  job_title: "상품기획/리테일 영업(MD)",
  company_id: 1,
  interview_date: "2025-11-22",
  scores: {
    final_score: 87.0,
    job_overall: 89.2,
    common_overall: 84.5,
    confidence_overall: 0.81,
    reliability_level: "high",
  },
  competencies: [
    { id: "JOB_01", name: "데이터 기반 인사이트 도출", category: "job", score: 92, confidence: 0.83, strengths: ["재고/판매/트렌드 3축 분석", "라인업 조정 후 KPI 개선 수치 제시"], weaknesses: ["신규 데이터 취득 비용/리스크 언급 부족"] },
    { id: "JOB_02", name: "전략적 문제해결", category: "job", score: 86, confidence: 0.78, strengths: ["주간 KPI 모니터링/피벗 사례 설명"], weaknesses: ["목표-실적 차이 대응 시 재무 임팩트 계산 없음"] },
    { id: "JOB_03", name: "밸류체인 최적화", category: "job", score: 81, confidence: 0.74, strengths: ["단가 재협상으로 마진 개선 사례 제시"], weaknesses: ["리드타임/품질 리스크 모니터링 설명 부족"] },
    { id: "JOB_04", name: "고객 여정 및 마케팅 전략", category: "job", score: 78, confidence: 0.72, strengths: ["타겟 고객 페르소나 정의"], weaknesses: ["마케팅 ROI 분석 미흡"] },
    { id: "JOB_05", name: "이해관계자 관리 및 협상", category: "job", score: 85, confidence: 0.80, strengths: ["데이터 기반 설득", "Win-Win 협상안 제시"], weaknesses: ["R&R 조정 과정 설명 부족"] },
    { id: "COMM_01", name: "문제해결력", category: "common", score: 88, confidence: 0.82, strengths: ["VOC/리뷰 데이터를 근거로 의사결정"], weaknesses: ["재구매/충성도 지표 활용 언급 없음"] },
    { id: "COMM_02", name: "성취/동기 역량", category: "common", score: 84, confidence: 0.79, strengths: ["높은 목표 설정 및 달성"], weaknesses: ["주도성 사례 부족"] },
    { id: "COMM_03", name: "성장 잠재력", category: "common", score: 82, confidence: 0.76, strengths: ["디자인팀과 데이터+브랜드 절충안 도출"], weaknesses: ["이해관계자별 KPI 정렬 과정이 짧음"] },
    { id: "COMM_04", name: "대인관계 역량", category: "common", score: 86, confidence: 0.81, strengths: ["명확한 커뮤니케이션"], weaknesses: ["갈등 해결 과정 상세 부족"] },
    { id: "COMM_05", name: "조직 적합성", category: "common", score: 80, confidence: 0.75, strengths: ["데이터 기반 의사결정 가치관 일치"], weaknesses: ["피드백 수용 사례 미흡"] },
  ],
  analysis_summary: {
    aggregator_summary: "데이터 기반 문제 정의와 실행력이 강점이며 디자인팀과의 협업에서 근거를 제시해 합의를 이끌었다. 밸류체인 최적화 경험도 있으나 리스크 관리 상세가 부족하다.",
    overall_applicant_summary: "데이터 중심 사고와 KPI 실행 경험이 뚜렷하며, 협업에서 근거 제시가 일관적이다. 다만 원가/리드타임 리스크 대응과 재무 임팩트 계산을 더 구체화할 필요가 있다.",
    positive_keywords: ["데이터 기반 문제 정의", "KPI 실행력", "이해관계자 설득"],
    negative_keywords: ["리스크 관리 세부 부족", "재무 임팩트 계산 보완 필요"],
    recommended_questions: [
      "리드타임 지연이나 품질 이슈를 사전에 탐지/관리한 구체적 사례가 있나요?",
      "목표-실적 차이를 재무 임팩트(매출/마진)로 환산해 대응한 경험을 설명해주세요.",
      "디자인/생산과 의견 충돌 시 KPI를 어떻게 정렬했는지 단계별로 말해주세요."
    ],
  },
};

export default candidateDetailMock;
