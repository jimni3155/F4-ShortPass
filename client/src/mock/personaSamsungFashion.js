const personaSamsungFashion = {
  company: {
    name: '삼성물산 패션부문',
    source_url: 'https://www.samsungcnt.com/about-us/careers.do',
  },
  personas: [
    {
      id: 'INT_01',
      persona_name: '김전략 수석',
      role: '패션 MD/영업 전략 15년차',
      type: '전략형 면접관',
      tone: '데이터 중심, 압박 20%',
      focus_keywords: ['데이터 기반 의사결정', '상품 포트폴리오', '매출·마진 개선'],
      questions: [
        '최근 시즌에서 매출 또는 마진을 개선한 사례를 데이터로 설명해 주세요.',
        '상품 포트폴리오를 조정했던 경험이 있다면, 의사결정 프레임과 결과를 공유해 주세요.',
      ],
    },
    {
      id: 'INT_02',
      persona_name: '박협업 팀장',
      role: '채널·협업 운영 12년차',
      type: '실행형 면접관',
      tone: '실무적, 구체적 예시 요구',
      focus_keywords: ['유관부서 협업', '갈등 조율', '밸류체인 운영'],
      questions: [
        '디자인·생산·영업 간 이해관계가 엇갈렸을 때 어떻게 합의했는지 구체적으로 말해 주세요.',
        '납기나 재고 이슈가 있었을 때 어떤 데이터와 소통 방식으로 해결했나요?',
      ],
    },
    {
      id: 'INT_03',
      persona_name: '이컬처 매니저',
      role: '조직문화/인재육성 HRBP 10년차',
      type: '조직적합형 면접관',
      tone: '정중·차분, 가치관·성장 탐색',
      focus_keywords: ['조직 적합성', '피드백 수용성', '학습 민첩성'],
      questions: [
        '피드백을 받고 행동을 바꿔 성과를 낸 사례를 말해 주세요.',
        '압박이 큰 시즌에 팀을 어떻게 유지하고 동기부여했나요?',
      ],
    },
  ],
  initial_questions: [
    '우리 브랜드의 최근 패션 트렌드를 어떻게 해석했고, 시즌 전략에 어떻게 반영할 수 있을지 말씀해 주세요.',
    '목표 대비 매출이 30% 미달할 때, 어떤 데이터부터 보고 어떤 우선순위로 대응 전략을 세우시겠습니까?',
    '의견 충돌이 있던 협업 상황을 하나 선택해, 문제 정의부터 합의 도출까지의 과정을 설명해 주세요.',
  ],
  // common_competencies: [
  //   {id: 'COMM_01', name: '고객지향'},
  //   {id: 'COMM_02', name: '도전정신'},
  //   {id: 'COMM_03', name: '협동·팀워크'},
  //   {id: 'COMM_04', name: '목표지향'},
  //   {id: 'COMM_05', name: '책임감'},
  // ],
  common_competencies: [
    {id: 'COMM_01', name: '성취/동기'},
    {id: 'COMM_02', name: '성장잠재력'},
    {id: 'COMM_03', name: '대인관계'},
    {id: 'COMM_04', name: '조직적합'},
    {id: 'COMM_05', name: '문제해결력'},
  ],
  // job_competencies: [
  //   {id: 'JOB_01', name: '매출·트렌드 데이터 분석 및 상품 기획'},
  //   {id: 'JOB_02', name: '시즌 전략 수립 및 비즈니스 문제해결'},
  //   {id: 'JOB_03', name: '소싱·생산·유통 밸류체인 최적화'},
  //   {id: 'JOB_04', name: '고객 여정 설계 및 VMD·마케팅 통합 전략'},
  //   {id: 'JOB_05', name: '유관부서 협업 및 이해관계자 협상'},
  // ],
  job_competencies: [
    {id: 'JOB_01', name: '데이터 분석'},
    {id: 'JOB_02', name: '시즌 전략 KPI'},
    {id: 'JOB_03', name: '이해관계자 협업'},
    {id: 'JOB_04', name: '가치사슬 최적합'},
    {id: 'JOB_05', name: '고객 여정 마케팅'},
  ],
};

export default personaSamsungFashion;
