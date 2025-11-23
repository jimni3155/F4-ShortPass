import {useState, useEffect} from 'react';
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
    total_applicants: 4, // 전체 인터뷰 완료 인원 수 (mock)
    applicants: [
      {
        applicant_id: 1,
        applicant_name: '김지원',
        interview_id: 90001,
        interview_date: '2025-03-10',
        interview_status: 'completed',
        school: '이화여자대학교',
        major: '의류학과',
        gpa: 3.9,
        scores: {
          final_score: 91.0,
          job_overall: 93.2,
          common_overall: 88.5,
          confidence_overall: 0.86,
        },
        // top_strengths: ['시즌 트렌드 분석', '매출·재고 데이터 기반 상품 구성'],
        // top_weaknesses: ['생산 리드타임 및 원가 구조 이해 부족'],
        ai_one_line_summary:
          '데이터 기반 MD로 재고회전율 0.8→1.2 개선(품절률 5%↓), 마진 35→38.5% 달성하며 원가·품질 리스크 관리, 디자인/VMD·공급업체 협업·협상에 강점이고 리스크 관리 체계 학습 의지가 명확한 지원자입니다.',
        is_highlighted: true,
      },
      {
        applicant_id: 2,
        applicant_name: '박민재',
        interview_id: 90002,
        interview_date: '2025-03-12',
        interview_status: 'completed',
        school: '연세대학교',
        major: '경영학과',
        gpa: 3.8,
        scores: {
          final_score: 87.5,
          job_overall: 88.7,
          common_overall: 85.3,
          confidence_overall: 0.79,
        },
        top_strengths: ['카테고리별 매출 분석', '리테일 운영 관점의 인사이트'],
        top_weaknesses: ['패션 소재·원단에 대한 기초 이해'],
        ai_one_line_summary:
          '리테일 영업 경험을 바탕으로 매장·현장 관점에서 상품 포트폴리오를 해석할 수 있는 지원자입니다.',
        is_highlighted: true,
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
          final_score: 82.0,
          job_overall: 80.5,
          common_overall: 83.2,
          confidence_overall: 0.74,
        },
        top_strengths: ['브랜드 포지셔닝 이해', '컬렉션 컨셉 스토리텔링'],
        top_weaknesses: ['정량 분석과 KPI 수립 경험 부족'],
        ai_one_line_summary:
          '브랜드·컬렉션 스토리 구성에 강점을 보이지만 수치 기반 기획은 보완 여지가 있는 지원자입니다.',
        is_highlighted: false,
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
          final_score: 78.5,
          job_overall: 79.0,
          common_overall: 77.3,
          confidence_overall: 0.71,
        },
        top_strengths: ['글로벌 마켓 리서치', '중국 시장 트렌드 파악'],
        top_weaknesses: ['내부 커뮤니케이션에서의 의사결정 드라이브'],
        ai_one_line_summary:
          '글로벌, 특히 중국 패션 시장 트렌드 인사이트가 강점인 지원자로 해외 리테일 확장에 기여 가능성이 있습니다.',
        is_highlighted: false,
      },
    ],
    total_count: 4, // 현재 응답에 포함된 전체 지원자 수
    page: 1,
    page_size: 20,
  };
}

async function fetchCompanyMatchingResult(jobId) {
  await new Promise((resolve) => setTimeout(resolve, 500));
  return getMockCompanyMatchingResult(jobId);
}

export default function CompanyResultPage() {
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
            <h1 className='text-2xl font-bold text-blue'>인터뷰 결과</h1>
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
            <div className='flex items-center gap-3 mb-6'>
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
            </div>

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
                    주목
                  </th>
                </tr>
              </thead>
              <tbody>
                {filteredApplicants?.map((applicant, idx) => (
                  <tr
                    key={applicant.applicant_id}
                    className={`border-b border-gray-100 hover:bg-gray-50 transition-colors cursor-pointer`}
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
                      {applicant.is_highlighted && (
                        <Badge variant='secondary'>주목 인재</Badge>
                      )}
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
