// Sample question bank
const questionBank = {
    common: [
        "자기소개를 부탁드립니다.",
        "이 포지션에 지원하게 된 동기는 무엇인가요?",
        "가장 도전적이었던 프로젝트에 대해 설명해주세요.",
        "팀에서 갈등이 발생했을 때 어떻게 해결하나요?",
        "5년 후 자신의 모습을 어떻게 그리고 계신가요?",
    ],
    technical: [
        "최근에 학습한 기술이나 도구는 무엇인가요?",
        "코드 리뷰 시 어떤 점을 중점적으로 보시나요?",
        "성능 최적화 경험에 대해 말씀해주세요.",
    ],
}

const sampleCompanies = [
    { name: "Google Korea", id: "1" },
    { name: "Naver", id: "2" },
    { name: "Kakao Corporation", id: "3" },
]

// Generate mock candidate results
const mockResults = [
    {
      id: "1",
      name: "김민준",
      score: 92,
      matchingScore: 87,
      reviewTag: "우선 검토",
      evaluation: "기술 역량이 뛰어나며 커뮤니케이션 능력도 우수함",
      education: "서울대학교 컴퓨터공학과",
      age: 28,
      gender: "남",
    },
    {
      id: "2",
      name: "이서연",
      score: 88,
      matchingScore: 91,
      reviewTag: "우선 검토",
      evaluation: "문제 해결 능력이 탁월하고 팀워크가 좋음",
      education: "연세대학교 경영학과",
      age: 26,
      gender: "여",
    },
    {
      id: "3",
      name: "박지훈",
      score: 75,
      matchingScore: 72,
      reviewTag: "보류",
      evaluation: "기본 역량은 있으나 경험이 다소 부족함",
      education: "고려대학교 전자공학과",
      age: 25,
      gender: "남",
    },
    {
      id: "4",
      name: "최유진",
      score: 85,
      matchingScore: 83,
      reviewTag: "우선 검토",
      evaluation: "창의적이고 학습 의지가 강함",
      education: "KAIST 산업디자인학과",
      age: 27,
      gender: "여",
    },
    {
      id: "5",
      name: "정현우",
      score: 62,
      matchingScore: 58,
      reviewTag: "제외",
      evaluation: "역량이 요구사항에 미치지 못함",
      education: "부산대학교 경제학과",
      age: 29,
      gender: "남",
    },
    {
      id: "6",
      name: "강수민",
      score: 79,
      matchingScore: 76,
      reviewTag: "보류",
      evaluation: "잠재력은 있으나 추가 검토 필요",
      education: "성균관대학교 심리학과",
      age: 24,
      gender: "여",
    },
  ];
