import {useState} from 'react';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  Radar,
  ResponsiveContainer,
  Legend,
} from 'recharts';

export default function ApplicantEvaluationPage() {
  const params = useParams();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState('common'); // 'common' or 'job'

  const applicant = {
    name: '김지원',
    position: 'HRD 컨설턴트',
    interviewDate: '2024.03.15',
    totalScore: 85,
    commonScores: {
      문제해결력: 4.4, // 인터뷰 설명 과정의 구조화 능력 강조
      '성취·실행력': 3.9,
      한계극복: 4.2,
      성장잠재력: 4.6,
      '주도성·영향력': 4.3,
      책임감: 4.2,
    },

    jobScores: {
      '교육컨설팅·제안': 4.4,
      '과정 운영·관리': 4.0,
      '클라이언트·강사·학습자 커뮤니케이션': 4.5,
      '제안서·보고서 작성': 3.9,
      '성과·데이터 기반 운영(KPI/만족도)': 3.7,
      '외국어 커뮤니케이션(영어/일본어)': 3.6,
    },

    analysis: `
인터뷰에서 가장 두드러진 강점은 문제를 구조화하는 속도와 답변의 논리적 전개 방식입니다. 
질문을 받았을 때 곧바로 결론-근거-사례의 틀을 적용해 정리하는 능력이 탁월하며, 
특히 교육 기획·운영 과정에서 발생했던 실제 문제 상황을 인터뷰 중 구체적인 시나리오로 설명해 
현장 이해도와 실무 감각을 충분히 보여줬습니다.

또한 강사 섭외·학습자 관리·고객사 요구 조율 등의 질문에 대해 단순 경험 나열이 아닌 
“당시 고려했던 선택지 → 의사결정 기준 → 실제 실행 → 사후 개선” 흐름을 명확하게 설명해 
실제 컨설턴트 업무에서 필요한 사고 구조를 갖추고 있음을 확인했습니다.

포트폴리오에 포함된 제안서는 기본적 완성도는 있으나 인터뷰에서 말한 내용과 비교해 
정량 지표나 프로젝트 난이도를 더 깊게 설명하지 못해 문서 자체의 설득력은 인터뷰 대비 약했습니다. 
서류 기반 역량보다는 인터뷰에서 보여준 논리적 사고와 대화 능력이 전체 평가에서 높은 비중을 차지했습니다.

외국어 커뮤니케이션은 실무 협의 수준에서는 충분해 보이지만, 
“계약 조율”이나 “복잡한 이해관계 조정” 같이 난이도 높은 상황을 설명하는 데 약간 제한이 있었습니다.
`,

    keywords: {
      positive: [
        '즉각적인 논리 구조화 능력',
        '문제 상황 설명의 구체성',
        '고객·강사·학습자 조율 경험',
        '답변의 명확한 기준 제시',
        '인터뷰 중 높은 집중력',
        '케이스 기반 사고',
      ],
      negative: [
        '정량지표 활용 깊이 부족',
        '포트폴리오 완성도 대비 인터뷰 의존도 높음',
        '고난도 외국어 커뮤니케이션 사례 부족',
      ],
    },

    recommendedQuestions: [
      '인터뷰에서 언급한 프로젝트 중, 가장 복합적인 이해관계자가 얽혀 있었던 사례를 다시 한 번 단계별로 설명해주세요. 당시 의사결정 기준은 무엇이었나요?',
      '교육 효과 분석 시 사용했던 정량 지표(만족도·학습·행동·성과) 중, 실제로 본인이 가장 중요하게 보는 지표와 그 이유는 무엇인가요?',
      '강사 또는 클라이언트 요구가 갑자기 변경된 상황에서 즉각적으로 판단하고 대응했던 사례를 자세히 설명해주세요.',
      '인터뷰에서 말씀하신 제안서 개선 포인트를 기반으로, 현재 버전에서 보완하고 싶은 한 가지를 직접 선택해 설명해 주세요.',
      '외국어로 진행된 실무 협의 경험 중, 난이도가 높았던 상황을 하나 선택해 당시 의사결정 과정과 결과를 설명해주세요.',
    ],
  };

  // Transform data for radar chart
  const commonChartData = Object.entries(applicant.commonScores).map(
    ([key, value]) => ({
      subject: key,
      score: value,
      fullMark: 5,
    })
  );

  const jobChartData = Object.entries(applicant.jobScores).map(
    ([key, value]) => ({
      subject: key,
      score: value,
      fullMark: 5,
    })
  );

  return (
    <div className='min-h-screen bg-gray-50'>
      {/* Header */}
      <div className='bg-white border-b'>
        <div className='max-w-7xl mx-auto px-8 py-6'>
          <button
            onClick={() => router.back()}
            className='text-sm text-gray-600 hover:text-gray-900 mb-4'>
            ← 목록으로 돌아가기
          </button>
          <div className='flex items-center justify-between'>
            <div>
              <h1 className='text-2xl font-semibold text-gray-900'>
                지원자 심사평
              </h1>
              <div className='flex items-center gap-4 mt-2 text-sm text-gray-600'>
                <span className='font-medium text-gray-900'>
                  {applicant.name}
                </span>
                <span>|</span>
                <span>{applicant.position}</span>
                <span>|</span>
                <span>면접일: {applicant.interviewDate}</span>
              </div>
            </div>
            <div className='text-right'>
              <div className='text-sm text-gray-600'>종합 점수</div>
              <div className='text-3xl font-bold text-blue-600'>
                {applicant.totalScore}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className='max-w-7xl mx-auto px-8 py-8'>
        <div className='grid grid-cols-1 lg:grid-cols-2 gap-6'>
          {/* Radar Charts Section */}
          <div className='bg-white rounded-xl border shadow-sm p-6'>
            {/* Tabs */}
            <div className='flex gap-8 border-b mb-6'>
              <button
                onClick={() => setActiveTab('common')}
                className={`pb-3 text-base font-medium transition-colors relative ${
                  activeTab === 'common'
                    ? 'text-gray-900'
                    : 'text-gray-500 hover:text-gray-700'
                }`}>
                공통 역량
                {activeTab === 'common' && (
                  <div className='absolute bottom-0 left-0 right-0 h-0.5 bg-gray-900' />
                )}
              </button>
              <button
                onClick={() => setActiveTab('job')}
                className={`pb-3 text-base font-medium transition-colors relative ${
                  activeTab === 'job'
                    ? 'text-gray-900'
                    : 'text-gray-500 hover:text-gray-700'
                }`}>
                직무 역량
                {activeTab === 'job' && (
                  <div className='absolute bottom-0 left-0 right-0 h-0.5 bg-gray-900' />
                )}
              </button>
            </div>

            {/* Common Competencies */}
            {activeTab === 'common' && (
              <div>
                <div className='mb-4'>
                  <h3 className='text-lg font-semibold text-gray-900 mb-1'>
                    공통역량 평가
                  </h3>
                  <p className='text-sm text-gray-600'>
                    AI가 면접 답변 기반으로 산출한 6개 영역 역량 점수입니다.
                  </p>
                </div>

                <ResponsiveContainer width='100%' height={400}>
                  <RadarChart data={commonChartData}>
                    <PolarGrid stroke='#e5e7eb' />
                    <PolarAngleAxis
                      dataKey='subject'
                      tick={{fill: '#4b5563', fontSize: 13}}
                    />
                    <Radar
                      name='역량 점수'
                      dataKey='score'
                      stroke='#ec4899'
                      fill='#ec4899'
                      fillOpacity={0.3}
                      strokeWidth={2}
                    />
                  </RadarChart>
                </ResponsiveContainer>

                {/* Score Table */}
                <div className='mt-6 space-y-2'>
                  {Object.entries(applicant.commonScores).map(
                    ([key, value]) => (
                      <div
                        key={key}
                        className='flex items-center justify-between text-sm'>
                        <span className='text-gray-700'>{key}</span>
                        <div className='flex items-center gap-3'>
                          <div className='w-32 bg-gray-200 rounded-full h-2'>
                            <div
                              className='bg-pink-500 h-2 rounded-full'
                              style={{width: `${(value / 5) * 100}%`}}
                            />
                          </div>
                          <span className='font-medium text-gray-900 w-8 text-right'>
                            {value.toFixed(1)}
                          </span>
                        </div>
                      </div>
                    )
                  )}
                </div>
              </div>
            )}

            {/* Job Competencies */}
            {activeTab === 'job' && (
              <div>
                <div className='mb-4'>
                  <h3 className='text-lg font-semibold text-gray-900 mb-1'>
                    직무역량 평가
                  </h3>
                  <p className='text-sm text-gray-600'>
                    JD 기반 직무 관련 6가지 핵심 역량 평가 결과입니다.
                  </p>
                </div>

                <ResponsiveContainer width='100%' height={400}>
                  <RadarChart data={jobChartData}>
                    <PolarGrid stroke='#e5e7eb' />
                    <PolarAngleAxis
                      dataKey='subject'
                      tick={{fill: '#4b5563', fontSize: 13}}
                    />
                    <Radar
                      name='직무 점수'
                      dataKey='score'
                      stroke='#06b6d4'
                      fill='#06b6d4'
                      fillOpacity={0.3}
                      strokeWidth={2}
                    />
                  </RadarChart>
                </ResponsiveContainer>

                {/* Score Table */}
                <div className='mt-6 space-y-2'>
                  {Object.entries(applicant.jobScores).map(([key, value]) => (
                    <div
                      key={key}
                      className='flex items-center justify-between text-sm'>
                      <span className='text-gray-700'>{key}</span>
                      <div className='flex items-center gap-3'>
                        <div className='w-32 bg-gray-200 rounded-full h-2'>
                          <div
                            className='bg-cyan-500 h-2 rounded-full'
                            style={{width: `${(value / 5) * 100}%`}}
                          />
                        </div>
                        <span className='font-medium text-gray-900 w-8 text-right'>
                          {value.toFixed(1)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right Column - Analysis & Keywords */}
          <div className='space-y-6'>
            {/* AI Analysis */}
            <div className='bg-white rounded-xl border shadow-sm p-6'>
              <h3 className='text-lg font-semibold text-gray-900 mb-4'>
                AI 심층 분석 심사평
              </h3>
              <p className='text-sm text-gray-700 leading-relaxed'>
                {applicant.analysis}
              </p>
            </div>

            {/* Keywords */}
            <div className='bg-white rounded-xl border shadow-sm p-6'>
              <h3 className='text-lg font-semibold text-gray-900 mb-4'>
                요약 평가 키워드
              </h3>

              <div className='mb-4'>
                <div className='text-sm text-gray-600 mb-2'>긍정</div>
                <div className='flex flex-wrap gap-2'>
                  {applicant.keywords.positive.map((keyword, index) => (
                    <span
                      key={index}
                      className='px-3 py-1.5 bg-green-50 text-green-700 text-sm rounded-full border border-green-200'>
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <div className='text-sm text-gray-600 mb-2'>부정</div>
                <div className='flex flex-wrap gap-2'>
                  {applicant.keywords.negative.map((keyword, index) => (
                    <span
                      key={index}
                      className='px-3 py-1.5 bg-red-50 text-red-700 text-sm rounded-full border border-red-200'>
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Recommended Questions */}
            <div className='bg-white rounded-xl border shadow-sm p-6'>
              <h3 className='text-lg font-semibold text-gray-900 mb-4'>
                추천 질문 목록
              </h3>
              <p className='text-sm text-gray-600 mb-4'>
                지원자의 답변을 바탕으로 AI가 생성한 심화 면접 질문입니다.
              </p>
              <ul className='space-y-3'>
                {applicant.recommendedQuestions.map((question, index) => (
                  <li key={index} className='flex gap-3 text-sm text-gray-700'>
                    <span className='text-blue-600 font-medium'>
                      {index + 1}.
                    </span>
                    <span>{question}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
