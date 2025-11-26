import {useEffect, useState} from 'react';
import samsungLogo from '@assets/images/samsung-logo.svg';
import InputField from '@components/InputField';
import Toggle from '@components/Toggle';
import Badge from '@components/Badge';
import {useNavigate} from 'react-router-dom';

function getMockCompanyMatchingResult(jobId) {
  return {
    job_id: jobId,
    job_title: '상품기획',
    company_id: 1,
    company_name: '삼성물산 패션부문',
    employment_type: '정규직',
    hiring_status: '진행중',
    interview_period: '2025.10.23 – 2025.12.15',
    total_applicants: 7, // 전체 인터뷰 완료 인원 수 (mock)
    applicants: [
      {
        applicant_id: 1,
        applicant_name: '김지원',
        interview_id: 90001,
        interview_date: '2025-10-27',
        interview_status: 'completed',
        school: '서울대학교',
        major: '의류학과',
        gpa: 3.8,
        scores: {
          final_score: 76.4,
          job_overall: 77.4,
          common_overall: 66.4,
          confidence_overall: 0.86,
        },
        // top_strengths: ['시즌 트렌드 분석', '매출·재고 데이터 기반 상품 구성'],
        // top_weaknesses: ['생산 리드타임 및 원가 구조 이해 부족'],
        ai_one_line_summary:
          '패션 도메인 이해와 데이터 기반 기획 역량이 균형 잡힌 상품기획형 인재입니다.',
        is_highlighted: true,
        is_bookmarked: true,
      },
      {
        applicant_id: 2,
        applicant_name: '박서진',
        interview_id: 90002,
        interview_date: '2025-03-21',
        interview_status: 'completed',
        school: '가천대학교',
        major: '패션디자인학과',
        gpa: 3.2,
        scores: {
          final_score: 69.5,
          job_overall: 68.0,
          common_overall: 70.3,
          confidence_overall: 0.69,
        },
        top_strengths: ['카테고리별 매출 분석', '리테일 운영 관점의 인사이트'],
        top_weaknesses: ['데이터 리터러시 부족', '브랜드 포지셔닝 이해 부족'],
        ai_one_line_summary:
          '현장 감각과 팀워크는 좋지만 데이터 분석과 기획 논리가 약해 추가 학습이 필요한 지원자입니다.',
        is_highlighted: false,
        is_bookmarked: true,
      },
      {
        applicant_id: 3,
        applicant_name: '이서윤',
        interview_id: 90003,
        interview_date: '2025-03-15',
        interview_status: 'completed',
        school: '성균관대학교',
        major: '글로벌리더학',
        gpa: 3.7,
        scores: {
          final_score: 65,
          job_overall: 62,
          common_overall: 70,
          confidence_overall: 0.74,
        },
        top_strengths: ['브랜드 포지셔닝 이해', '컬렉션 컨셉 스토리텔링'],
        top_weaknesses: ['정량 분석과 KPI 수립 경험 부족'],
        ai_one_line_summary:
          '브랜드·컬렉션 스토리 구성에 강점을 보이지만 수치 기반 기획은 보완 여지가 있는 지원자입니다.',
        is_highlighted: false,
        is_bookmarked: false,
      },
      {
        applicant_id: 4,
        applicant_name: '정하늘',
        interview_id: 90004,
        interview_date: '2025-03-18',
        interview_status: 'completed',
        school: '한국외국어대학교',
        major: '중국어과',
        gpa: 3.6,
        scores: {
          final_score: 72,
          job_overall: 75.4,
          common_overall: 63,
          confidence_overall: 0.71,
        },
        top_strengths: ['글로벌 마켓 리서치', '중국 시장 트렌드 파악'],
        top_weaknesses: ['내부 커뮤니케이션에서의 의사결정 드라이브'],
        ai_one_line_summary:
          '글로벌, 특히 중국 패션 시장 트렌드 인사이트가 강점인 지원자로 해외 리테일 확장에 기여 가능성이 있습니다.',
        is_highlighted: false,
        is_bookmarked: false,
      },
      {
        applicant_id: 5,
        applicant_name: '최민수',
        interview_id: 90005,
        interview_date: '2025-03-22',
        interview_status: 'completed',
        school: '부산대학교',
        major: '경제학과',
        gpa: 3.0,
        scores: {
          final_score: 62.3,
          job_overall: 61.0,
          common_overall: 63.5,
          confidence_overall: 0.62,
        },
        top_strengths: ['수요 예측 기본 이해', '정리된 커뮤니케이션'],
        top_weaknesses: ['패션 산업 지식 부족', '주도적 실행 사례 부족'],
        ai_one_line_summary:
          '기초 정량 감각은 있으나 패션 도메인 경험과 실행 드라이브가 부족해 멘토링이 필요한 지원자입니다.',
        is_highlighted: false,
        is_bookmarked: false,
      },
      {
        applicant_id: 6,
        applicant_name: '윤하나',
        interview_id: 90006,
        interview_date: '2025-03-24',
        interview_status: 'completed',
        school: '경기대학교',
        major: '영문학과',
        gpa: 2.8,
        scores: {
          final_score: 58.4,
          job_overall: 57.0,
          common_overall: 59.2,
          confidence_overall: 0.58,
        },
        top_strengths: ['고객 응대 경험', '팀 플레이'],
        top_weaknesses: ['데이터 분석 역량 부족', '패션 트렌드 이해 부족'],
        ai_one_line_summary:
          '서비스 마인드는 있으나 직무 적합성과 정량 역량이 낮아 추가 교육이 필수적인 지원자입니다.',
        is_highlighted: false,
        is_bookmarked: false,
      },
      {
        applicant_id: 7,
        applicant_name: '오상민',
        interview_id: 90007,
        interview_date: '2025-03-25',
        interview_status: 'completed',
        school: '청주대학교',
        major: '무역학과',
        gpa: 3.1,
        scores: {
          final_score: 60.7,
          job_overall: 59.5,
          common_overall: 62.0,
          confidence_overall: 0.6,
        },
        top_strengths: ['원가 협상 기초 경험', '성실한 태도'],
        top_weaknesses: ['패션 도메인 이해 부족', '데이터 기반 기획 경험 부족'],
        ai_one_line_summary:
          '원가 감각은 있지만 패션 상품기획 역량과 정량 설득력이 부족한 초기 단계 지원자입니다.',
        is_highlighted: false,
        is_bookmarked: false,
      },
    ],
    total_count: 7, // 현재 응답에 포함된 전체 지원자 수
    page: 1,
    page_size: 20,
  };
}

async function fetchCompanyMatchingResult(jobId) {
  await new Promise((resolve) => setTimeout(resolve, 500));
  return getMockCompanyMatchingResult(jobId);
}

export default function InterviewResult() {
  const navigate = useNavigate();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [schoolFilter, setSchoolFilter] = useState('');
  const [majorFilter, setMajorFilter] = useState('');
  const [minGpa, setMinGpa] = useState('');
  const [minFinalScore, setMinFinalScore] = useState('');
  const [minJobScore, setMinJobScore] = useState('');
  const [minCoreScore, setMinCoreScore] = useState('');
  const [showHighlightOnly, setShowHighlightOnly] = useState(false);

  const jobId = 101;

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const data = await fetchCompanyMatchingResult(jobId);
        setResult(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [jobId]);

  const filteredApplicants = result?.applicants.filter((applicant) => {
    const matchesSchool =
      !schoolFilter || applicant.school.includes(schoolFilter);
    const matchesMajor = !majorFilter || applicant.major.includes(majorFilter);
    const matchesGpa = !minGpa || applicant.gpa >= Number.parseFloat(minGpa);
    const matchesFinalScore =
      !minFinalScore ||
      applicant.scores.final_score >= Number.parseInt(minFinalScore);
    const matchesJobScore =
      !minJobScore ||
      applicant.scores.job_overall >= Number.parseInt(minJobScore);
    const matchesCoreScore =
      !minCoreScore ||
      applicant.scores.common_overall >= Number.parseInt(minCoreScore);
    const matchesHighlight = !showHighlightOnly || applicant.is_highlighted;

    return (
      matchesSchool &&
      matchesMajor &&
      matchesGpa &&
      matchesFinalScore &&
      matchesJobScore &&
      matchesCoreScore &&
      matchesHighlight
    );
  });

  const uniqueSchools = [
    ...new Set(result?.applicants.map((a) => a.school) || []),
  ];

  return (
    <div className='min-h-screen'>
      <div className='container mx-auto px-12 py-8 max-w-[1800px]'>
        {/* 헤더 섹션 */}
        <div className='flex items-center justify-between mb-8 pb-6 border-b border-gray-200'>
          <div>
            <h1 className='text-2xl font-bold text-blue'>면접 인사이트</h1>
          </div>
        </div>

        {/* 기업 정보 */}
        <div className='mb-8 pb-6 border-b border-gray-200'>
          <div className='flex items-start gap-4 mb-4'>
            <div className='w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center shrink-0'>
              <img src={samsungLogo} alt='Company Logo' className='w-8 h-8' />
            </div>
            <div className='flex-1'>
              <div className='flex items-center gap-2 mb-1'>
                <h2 className='text-xl font-bold text-gray-900'>
                  {result?.company_name}
                </h2>
                <Badge
                  variant='ghost'
                  classname='text-xs font-medium bg-gray-200 px-2'>
                  {result?.employment_type}
                </Badge>
                <Badge classname='text-xs font-medium bg-green-100 text-green-700 px-2 rounded-full'>
                  {result?.hiring_status}
                </Badge>
              </div>
              <h3 className='text-base font-medium text-gray-700'>
                {result?.job_title}
              </h3>
            </div>
          </div>
          <div className='flex gap-6 text-sm text-gray-600 pl-16'>
            <div>
              <span className='text-gray-500'>모집 기간:</span>{' '}
              <span className='font-medium text-gray-900'>
                {result?.interview_period}
              </span>
            </div>
            <div>
              <span className='text-gray-500'>전체 지원자:</span>{' '}
              <span className='font-medium text-gray-900'>
                {result?.total_applicants}명
              </span>
            </div>
          </div>
        </div>

        {/* 필터링 영역 */}
        <div className='mb-6 pb-6 border-b border-gray-200'>
          <div className='flex items-center justify-between mb-4'>
            <h3 className='text-sm font-semibold text-gray-700'>필터</h3>
            <button
              onClick={() => {
                setSchoolFilter('');
                setMajorFilter('');
                setMinGpa('');
                setMinFinalScore('');
                setMinJobScore('');
                setMinCoreScore('');
                setShowHighlightOnly(false);
              }}
              className='text-sm text-blue-600 hover:text-blue-700 font-medium'>
              초기화
            </button>
          </div>

          <div className='space-y-3'>
            {/* 학력 관련 */}
            <div className='flex items-center gap-3'>
              <span className='text-sm text-gray-600 w-20 shrink-0'>
                학력 정보
              </span>
              <div className='flex-1 flex gap-3'>
                <InputField
                  type='text'
                  placeholder='학교 (예: 숙명여자대학교)'
                  value={schoolFilter}
                  onChange={(e) => setSchoolFilter(e.target.value)}
                  classname='w-100 text-sm'
                />

                <InputField
                  type='text'
                  placeholder='전공 (예: 경영학)'
                  value={majorFilter}
                  onChange={(e) => setMajorFilter(e.target.value)}
                  classname='w-100 text-sm'
                />

                <InputField
                  type='number'
                  step='0.1'
                  placeholder='최소 학점 (예: 3.5)'
                  value={minGpa}
                  onChange={(e) => setMinGpa(e.target.value)}
                  classname='text-sm'
                />
              </div>
            </div>

            {/* 매칭 점수 관련 */}
            {/* <div className='flex items-center gap-3 mb-6'>
              <span className='text-sm text-gray-600 w-20 shrink-0'>
                점수 범위
              </span>
              <div className='flex-1 flex gap-3'>
                <InputField
                  type='number'
                  placeholder='최종 매칭 최소값'
                  value={minFinalScore}
                  onChange={(e) => setMinFinalScore(e.target.value)}
                  classname='w-60 text-sm'
                />

                <InputField
                  type='number'
                  placeholder='직무 역량 최소값'
                  value={minJobScore}
                  onChange={(e) => setMinJobScore(e.target.value)}
                  classname='w-60 text-sm'
                />

                <InputField
                  type='number'
                  placeholder='핵심 역량 최소값'
                  value={minCoreScore}
                  onChange={(e) => setMinCoreScore(e.target.value)}
                  classname='w-60 text-sm'
                />
              </div>
            </div> */}

            {/* Highlight Toggle */}
            <div className='flex items-center gap-3'>
              <span className='text-sm text-gray-600 w-20 shrink-0'></span>
              <div className='flex items-center gap-2'>
                <Toggle
                  id='highlight-toggle'
                  label='주목 인재만 보기'
                  checked={showHighlightOnly}
                  onChange={() => setShowHighlightOnly((prev) => !prev)}
                />
              </div>
            </div>
          </div>
        </div>

        {/* 필터 결과 지원자 수 */}
        <div className='flex items-center justify-between mb-4'>
          <p className='text-sm text-gray-600'>
            총{' '}
            <span className='font-semibold text-gray-900'>
              {filteredApplicants?.length || 0}
            </span>
            명
          </p>
        </div>

        {/* 테이블 */}
        <div className='border border-gray-200 rounded-lg overflow-hidden'>
          <div className='overflow-x-auto'>
            <table className='w-full'>
              <thead>
                <tr className='border-b border-gray-200 bg-white'>
                  <th className='px-4 py-3 text-left text-xs font-medium text-gray-600'>
                    지원자명
                  </th>
                  <th className='px-4 py-3 text-left text-xs font-medium text-gray-600'>
                    학교 / 전공
                  </th>
                  <th className='px-4 py-3 text-center text-xs font-medium text-gray-600'>
                    학점
                  </th>
                  <th className='px-4 py-3 text-center text-xs font-medium text-gray-600'>
                    면접일
                  </th>
                  <th className='px-4 py-3 text-center text-xs font-medium text-gray-600'>
                    최종 점수
                  </th>
                  <th className='px-4 py-3 text-center text-xs font-medium text-gray-600'>
                    직무 역량
                  </th>
                  <th className='px-4 py-3 text-center text-xs font-medium text-gray-600'>
                    핵심 역량
                  </th>
                  <th className='px-4 py-3 text-left text-xs font-medium text-gray-600'>
                    AI 한줄 평가
                  </th>
                  <th className='px-4 py-3 text-center text-xs font-medium text-gray-600'>
                    주목/북마크
                  </th>
                </tr>
              </thead>
              <tbody>
                {filteredApplicants?.map((applicant, idx) => (
                  <tr
                    key={applicant.applicant_id}
                    className={`border-b border-gray-100 bg-white hover:bg-gray-50 transition-colors cursor-pointer`}
                    onClick={() =>
                      navigate(`/company/applicant/${applicant.applicant_id}`)
                    }>
                    <td className='px-4 py-3 whitespace-nowrap'>
                      <span className='text-sm font-medium text-gray-900'>
                        {applicant.applicant_name}
                      </span>
                    </td>
                    <td className='px-4 py-3'>
                      <div className='text-sm'>
                        <div className='font-medium text-gray-900'>
                          {applicant.school}
                        </div>
                        <div className='text-gray-500 text-xs'>
                          {applicant.major}
                        </div>
                      </div>
                    </td>
                    <td className='px-4 py-3 text-center whitespace-nowrap'>
                      <span className='text-sm font-medium text-gray-900'>
                        {applicant.gpa.toFixed(1)}
                      </span>
                    </td>
                    <td className='px-4 py-3 text-center whitespace-nowrap'>
                      <span className='text-sm text-gray-600'>
                        {applicant.interview_date}
                      </span>
                    </td>
                    <td className='px-4 py-3 text-center whitespace-nowrap'>
                      <span className='text-sm font-semibold text-blue'>
                        {applicant.scores.final_score}
                      </span>
                    </td>
                    <td className='px-4 py-3 text-center whitespace-nowrap'>
                      <span className='text-sm font-semibold text-[#50C878]'>
                        {applicant.scores.job_overall}
                      </span>
                    </td>
                    <td className='px-4 py-3 text-center whitespace-nowrap'>
                      <span className='text-sm font-semibold text-[#FFA500]'>
                        {applicant.scores.common_overall}
                      </span>
                    </td>
                  <td className='px-4 py-3 max-w-xs'>
                    <span className='text-sm text-gray-700 line-clamp-2'>
                      {applicant.ai_one_line_summary}
                    </span>
                  </td>
                  <td className='px-3 py-3 text-center whitespace-nowrap'>
                    <div className='flex items-center justify-center gap-2'>
                      {applicant.is_highlighted && (
                        <Badge variant='secondary'>주목 인재</Badge>
                      )}
                      {applicant.is_bookmarked && (
                        <Badge
                          variant='ghost'
                          classname='px-2 py-1 rounded-lg border border-amber-200 bg-amber-50 text-amber-700 text-xs font-medium'>
                          북마크
                        </Badge>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
