# 프론트엔드 JSON 샘플 (채아용)

> 프론트엔드 개발을 위한 API 응답 샘플 및 데이터 구조

---

## 샘플 파일 위치

| 파일명 | 경로 | 용도 |
|--------|------|------|
| transcript_official_sample.json | `/server/test_data/` | 면접 트랜스크립트 |
| evaluation_response_sample.json | `/server/test_data/` | 평가 결과 응답 |
| persona_data.json | `/server/assets/` | 페르소나 정의 |

---

## 1. 평가 결과 (CandidateDetailPage용)

### 사용처
- `CandidateDetailPage.jsx` - 지원자 상세 결과 화면

### 주요 필드

```javascript
const evaluationData = {
  // 기본 정보
  interview_id: 90001,
  applicant_id: 101,
  applicant_name: "김지원",
  job_id: 1,
  job_title: "상품기획/리테일 영업(MD)",
  interview_date: "2025-11-22",

  // 점수 요약 (헤더 표시)
  scores: {
    final_score: 87.0,      // 총합 점수 (100점 만점)
    job_overall: 89.2,      // 직무 역량 평균
    common_overall: 84.5,   // 공통 역량 평균
    confidence_overall: 0.81, // 신뢰도 (0~1)
    reliability_level: "high" // high/medium/low
  },

  // 역량 배열 (레이더 차트 + 막대 그래프)
  competencies: [
    {
      id: "JOB_01",
      name: "데이터 기반 인사이트 도출",
      category: "job",        // "job" 또는 "common"
      score: 92,              // 0~100
      confidence: 0.83,       // 0~1
      strengths: ["강점1", "강점2"],
      weaknesses: ["약점1"]
    },
    // ... 총 10개 (job 5개 + common 5개)
  ],

  // AI 분석 요약
  analysis_summary: {
    aggregator_summary: "AI 심층 분석 텍스트...",
    overall_applicant_summary: "전체 요약 텍스트...",
    positive_keywords: ["데이터 기반", "KPI 실행력"],
    negative_keywords: ["리스크 관리 부족"],
    recommended_questions: [
      "추천 질문 1",
      "추천 질문 2",
      "추천 질문 3"
    ]
  }
};
```

### 사용 예시

```jsx
// 점수 표시
<p>{data.scores?.final_score}</p>

// 레이더 차트 데이터
const jobCompetencies = data.competencies.filter(c => c.category === 'job');
const commonCompetencies = data.competencies.filter(c => c.category === 'common');

// 막대 그래프 width
<div style={{ width: `${item.score}%` }} />

// 키워드 뱃지
{data.analysis_summary.positive_keywords.map(kw => (
  <span className="badge-positive">{kw}</span>
))}
```

---

## 2. 지원자 목록 (CandidateListPage용)

### 사용처
- `CandidateListPage.jsx` - 지원자 목록 화면

### 주요 필드

```javascript
const applicantListData = {
  job_id: 1,
  job_title: "상품기획/리테일 영업(MD)",
  applicants: [
    {
      applicant_id: 101,
      applicant_name: "김지원",
      interview_id: 90001,
      interview_date: "2025-11-22",
      interview_status: "completed",  // pending | in_progress | completed | evaluating
      scores: {
        final_score: 87.0,
        job_overall: 89.2,
        common_overall: 84.5
      },
      top_strengths: ["데이터 기반 문제 정의"],
      top_weaknesses: ["리스크 관리 세부 부족"]
    },
    // ... 더 많은 지원자
  ],
  total_count: 10
};
```

### 상태별 UI 처리

```jsx
const statusBadge = {
  pending: { text: "면접 예정", color: "gray" },
  in_progress: { text: "면접 중", color: "blue" },
  evaluating: { text: "평가 중", color: "yellow" },
  completed: { text: "완료", color: "green" }
};
```

---

## 3. 역량 ID 매핑

### 공통 역량 (category: "common")

| ID | 표시 이름 | 영문 Key |
|----|----------|----------|
| COMM_01 | 문제해결력 | problem_solving |
| COMM_02 | 성취/동기 역량 | achievement_motivation |
| COMM_03 | 성장 잠재력 | growth_potential |
| COMM_04 | 대인관계 역량 | interpersonal_skill |
| COMM_05 | 조직 적합성 | organizational_fit |

### 직무 역량 (category: "job")

| ID | 표시 이름 | 영문 Key |
|----|----------|----------|
| JOB_01 | 데이터 기반 인사이트 도출 | data_insight |
| JOB_02 | 전략적 문제해결 | strategic_problem_solving |
| JOB_03 | 밸류체인 최적화 | value_chain_optimization |
| JOB_04 | 고객 여정 및 마케팅 전략 | customer_journey_marketing |
| JOB_05 | 이해관계자 관리 및 협상 | stakeholder_management |

---

## 4. 차트 설정 가이드

### 레이더 차트 (Recharts)

```jsx
<RadarChart data={radarData}>
  <PolarGrid />
  <PolarAngleAxis dataKey="name" />
  <PolarRadiusAxis
    domain={[0, 100]}  // 100점 만점
    tickCount={6}
  />
  <Radar
    dataKey="score"
    stroke={category === 'common' ? '#ec4899' : '#3b82f6'}
    fill={category === 'common' ? '#ec4899' : '#3b82f6'}
    fillOpacity={0.3}
  />
</RadarChart>
```

### 막대 그래프

```jsx
// 점수를 직접 %로 사용 (0~100)
<div
  className="bg-blue-500 h-2.5 rounded-full"
  style={{ width: `${item.score}%` }}
/>
```

---

## 5. 색상 가이드

| 용도 | 색상 코드 | Tailwind |
|------|----------|----------|
| 직무 역량 | #3b82f6 | blue-500 |
| 공통 역량 | #ec4899 | pink-500 |
| 긍정 키워드 배경 | #ecfeff | cyan-50 |
| 긍정 키워드 텍스트 | #0e7490 | cyan-700 |
| 부정 키워드 배경 | #fef2f2 | red-50 |
| 부정 키워드 텍스트 | #dc2626 | red-600 |

---

## 6. API 연동 시 변경점

현재 Mock → API 전환 시 변경 필요:

```jsx
// Before (Mock)
useEffect(() => {
  setData(mockDetailData);
  setLoading(false);
}, [applicantId]);

// After (API)
useEffect(() => {
  const fetchData = async () => {
    try {
      const response = await fetch(`/api/evaluation/${interviewId}`);
      const data = await response.json();
      setData(data);
    } catch (error) {
      console.error('Failed to fetch evaluation:', error);
    } finally {
      setLoading(false);
    }
  };
  fetchData();
}, [interviewId]);
```

---

*생성일: 2025-11-22*
*작성: 지원 (AI 시스템)*
