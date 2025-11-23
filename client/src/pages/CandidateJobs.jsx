import Button from '@components/Button';
import {useNavigate} from 'react-router-dom';
import externalLink from '@assets/svg/external_link.svg';

// 지원자가 선택한 희망 직무
const selectedSubRoles = ['경영 기획', '영업 전략', '전략 컨설팅'];

const availableCompanies = [
  {
    id: 1,
    companyName: '삼성물산 패션부문',
    jobTitle: '상품기획(MD) 신입',
    deadline: '2025.12.15',
    matchedSubRoles: ['상품기획', '브랜드 기획', '마케팅'],
    requiredSkills: [
      '패션 트렌드 분석',
      '브랜드 기획',
      '시장 조사',
      '캠페인 기획',
      '소비자 분석',
    ],
    recommendationReason:
      '트렌드 기반의 상품 기획과 브랜드 운영 전략에 관심이 있다면 적합한 포지션입니다.',
    jobPostingUrl: 'https://example.com/job/7',
  },
  {
    id: 2,
    companyName: '삼성SDS',
    jobTitle: 'B2B 영업 전략 신입채용',
    deadline: '2025.12.02',
    matchedSubRoles: ['영업 전략'],
    requiredSkills: [
      'B2B 영업 전략 수립',
      '제안서 작성',
      '고객 커뮤니케이션',
      '시장 분석',
    ],
    recommendationReason: '영업 전략 중심으로 경험을 쌓을 수 있는 직무입니다.',
    jobPostingUrl: 'https://example.com/job/2',
  },
  {
    id: 3,
    companyName: 'LG CNS',
    jobTitle: '경영기획(사업전략) 신입/주니어',
    deadline: '2026.01.18',
    matchedSubRoles: ['경영 기획', '전략 컨설팅'],
    requiredSkills: ['경영 기획', '전략 수립', '재무 분석', '보고서 작성'],
    recommendationReason:
      '경영 기획과 전략 기획을 함께 경험할 수 있는 포지션이에요.',
    jobPostingUrl: 'https://example.com/job/3',
  },
  {
    id: 4,
    companyName: 'KB국민은행',
    jobTitle: '영업기획·채널전략 신입',
    deadline: '2025.12.22',
    matchedSubRoles: ['영업 전략', '경영 기획'],
    requiredSkills: ['영업 전략 수립', '시장 분석', 'KPI 관리', '기획력'],
    recommendationReason: '데이터 기반 영업 전략 기획 경험을 쌓을 수 있어요.',
    jobPostingUrl: 'https://example.com/job/4',
  },
  {
    id: 5,
    companyName: '딜로이트 안진회계법인',
    jobTitle: 'Business Analyst (BA) – Strategy & Operations',
    deadline: '2025.11.30',
    matchedSubRoles: ['전략 컨설팅', '경영 기획', '영업 전략'],
    requiredSkills: ['리서치', '전략 분석', '프로젝트 관리', '비즈니스 모델링'],
    recommendationReason:
      '선택한 기획/전략/컨설팅 역량을 모두 활용할 수 있어요.',
    jobPostingUrl: 'https://example.com/job/5',
  },
  {
    id: 6,
    companyName: 'CJ ENM',
    jobTitle: '전략기획팀 (주니어 경력)',
    deadline: '2025.12.05',
    matchedSubRoles: ['경영 기획', '전략 컨설팅'],
    requiredSkills: ['전략 기획', '사업 분석', '시장 조사', '재무 분석'],
    recommendationReason:
      '콘텐츠/엔터 업계에서 전략 경험을 쌓고 싶은 분께 적합해요.',
    jobPostingUrl: 'https://example.com/job/6',
  },
  {
    id: 7,
    companyName: '삼정KPMG',
    jobTitle: '전략·경영 컨설팅 어소시에이트 (신입)',
    deadline: '2025.12.20',
    matchedSubRoles: ['전략 컨설팅', '경영 기획'],
    requiredSkills: ['경영 전략', '문제 해결', '분석적 사고', '데이터 분석'],
    recommendationReason: "선택한 '전략 컨설팅' 경험과 잘 맞는 포지션이에요.",
    jobPostingUrl: 'https://example.com/job/1',
  },
];

export default function CandidateJobs() {
  const navigate = useNavigate();

  const handleStartInterview = (companyId) => {
    const company = availableCompanies.find((c) => c.id === companyId);
    console.log('start interview with companyId', companyId);
    navigate('/candidate/start');
  };

  const handleViewJobPosting = (url) => {
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  const handleGoBack = () => {
    navigate('/candidate/info');
  };

  return (
    <div className='min-h-screen'>
      <div className='max-w-4xl mx-auto px-6 py-16'>
        {/* 헤더 영역 */}
        <div className='text-center mb-12'>
          <h1 className='text-3xl md:text-4xl font-bold text-blue mb-4'>
            지원할 회사를 선택하세요
          </h1>
          <p className='text-base md:text-lg text-gray-600 mb-2'>
            선택하신 희망 직무를 기준으로 참여 가능한 회사를 추천해 드렸어요.
          </p>
        </div>

        {/* 요약 정보 */}
        <div className='mb-6'>
          <p className='text-sm text-slate-500'>
            총 {availableCompanies.length}개 회사
          </p>
        </div>

        {/* 회사 선택 카드 그리드 */}
        <div className='grid grid-cols-1 md:grid-cols-2 gap-4 mb-8'>
          {availableCompanies.map((company) => {
            return (
              <div
                key={company.id}
                className='bg-transparent border border-slate-200 rounded-2xl px-5 py-4'>
                {/* 모집 중 tag and header */}
                <div className='flex items-start justify-between mb-2.5'>
                  <div className='flex items-center gap-2'>
                    <h3 className='font-semibold text-base md:text-lg text-blue'>
                      {company.companyName}
                    </h3>
                  </div>
                  <div className='text-dark text-sm font-semibold px-3 py-1.5 whitespace-nowrap ml-2'>
                    ~ {company.deadline}
                  </div>
                </div>

                {/* 포지션명 */}
                <p className='font-medium text-gray-800 mb-3'>
                  {company.jobTitle}
                </p>

                {/* 매칭된 직무 */}
                <div className='mb-3'>
                  <p className='text-xs text-slate-600 mb-1.5'>매칭된 직무</p>
                  <div className='flex flex-wrap gap-1.5'>
                    {company.matchedSubRoles.map((role, idx) => (
                      <span
                        key={idx}
                        className='inline-block bg-blue-50 text-blue-700 text-xs px-2 py-1 rounded-full'>
                        {role}
                      </span>
                    ))}
                  </div>
                </div>

                {/* 주요 요구 스킬 */}
                <div className='mb-3'>
                  <p className='text-xs text-slate-600 mb-1.5'>
                    주요 요구 스킬
                  </p>
                  <div className='flex flex-wrap gap-1.5'>
                    {company.requiredSkills.slice(0, 4).map((skill, idx) => (
                      <span
                        key={idx}
                        className='inline-block bg-slate-100 text-slate-700 text-xs px-2 py-1 rounded-full'>
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                {/* 추천 이유 */}
                <p className='text-xs text-slate-600 leading-relaxed mb-4'>
                  {company.recommendationReason}
                </p>

                <div className='flex gap-2'>
                  <button
                    onClick={() => handleViewJobPosting(company.jobPostingUrl)}
                    className='flex-1 flex items-center justify-center gap-1.5 border border-slate-300 text-slate-700 text-sm font-medium py-2 px-3 rounded-lg hover:bg-slate-50 transition-colors'>
                    <img
                      src={externalLink}
                      alt='채용공고 확인'
                      className='w-3.5 h-3.5'
                    />
                    채용공고 보기
                  </button>
                  <button
                    onClick={() => handleStartInterview(company.id)}
                    className='flex-1 cursor-pointer bg-blue-100 hover:bg-blue text-dark hover:text-white text-sm font-medium py-2 px-3 rounded-lg transition-colors'>
                    면접 보기
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        {/* 안내 문구 */}
        <div className='bg-blue-50 border border-blue-100 rounded-lg px-4 py-3 mb-8'>
          <p className='text-sm text-blue-800'>
            면접 보기를 누르면 바로 면접 대기 화면으로 이동합니다.
          </p>
        </div>

        {/* 하단 버튼 */}
        <div className='flex justify-start'>
          <Button variant='ghost' onClick={handleGoBack}>
            이전
          </Button>
        </div>
      </div>
    </div>
  );
}
