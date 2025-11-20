import {useState, useEffect} from 'react';
import Button from '../components/Button';
import Badge from '../components/Badge';
import up from '../assets/svg/chevron-up.svg';
import down from '../assets/svg/chevron-down.svg';
import {useParams} from 'react-router-dom';
import API_V1 from '../lib/apiConfig';

async function fetchCompanyMatchingResult(jobId, {signal} = {}) {
  if (!jobId) throw new Error('유효하지 않은 공고 ID');

  const res = await fetch(`${API_V1}/company/jobs/${jobId}`, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
    signal,
  });

  if (!res.ok) {
    // FastAPI 에러 메시지 통과
    const text = await res.text().catch(() => '');
    const msg = text || `요청 실패 (${res.status})`;
    throw new Error(msg);
  }
  return res.json();
}

export default function CompanyResultPage() {
  const {jobId: jobIdParam} = useParams(); // /company/result/:jobId
  const jobId = Number(jobIdParam ?? 101); // 라우트에 없으면 임시 101

  const [result, setResult] = useState(null);
  const [expandedCards, setExpandedCards] = useState(new Set());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const controller = new AbortController();

    (async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchCompanyMatchingResult(jobId, {
          signal: controller.signal,
        });
        setResult(data);
      } catch (err) {
        // AbortError는 무시 (컴포넌트 언마운트 시 정상적인 동작)
        if (err.name === 'AbortError') {
          console.log('요청이 취소되었습니다 (정상)');
          return;
        }
        setError(err instanceof Error ? err.message : '에러가 발생했습니다.');
      } finally {
        setLoading(false);
      }
    })();

    return () => controller.abort();
  }, [jobId]);

  const toggleCard = (id) => {
    console.log('Toggling card for applicant ID:', id);
    const newExpanded = new Set(expandedCards);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedCards(newExpanded);
  };

  if (loading) {
    return (
      <div className='min-h-screen flex items-center justify-center'>
        <div className='text-muted-foreground'>로딩 중...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className='min-h-screen flex items-center justify-center'>
        <div className='text-center'>
          <p className='text-red-600 mb-4'>{error}</p>
          <Button onClick={() => window.location.reload()}>다시 시도</Button>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className='min-h-screen flex items-center justify-center'>
        <p>데이터를 찾을 수 없습니다.</p>
      </div>
    );
  }

  const isBlindMode =
    result.applicants.length > 0 && result.applicants[0].age === null;

  return (
    <div className='min-h-screen relative'>
      <div className='container mx-auto px-4 py-12 max-w-7xl'>
        <div className='mb-8'>
          <h1 className='text-center text-3xl font-bold text-gray-900 mb-2'>
            지원자 결과
          </h1>
          <p className=''>
            {result.company_name} - 총 {result.total_applicants}명의 지원자
          </p>
        </div>

        <div className='space-y-3'>
          {result.applicants.map((applicant) => {
            console.log('Rendering applicant:', applicant);
            const isHighScore = applicant?.match_score?.total_score >= 70;
            return (
              <div
                key={applicant?.applicant_id}
                className={`rounded-lg border overflow-hidden hover:shadow-md transition-all ${
                  isHighScore
                    ? 'bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-300 shadow-md'
                    : 'bg-transparent border-gray-300 shadow-sm'
                }`}>
                {/* Horizontal Row Layout */}
                <div className='flex items-center gap-6 p-4'>
                  {/* Name with Rank */}
                  <div className='px-2 w-28'>
                    <h3 className='font-medium'>
                      #{applicant?.rank} {applicant?.applicant_name}
                    </h3>
                  </div>

                  {/* 매칭 점수 */}
                  <div className='w-24 text-center'>
                    <div className='text-xs text-muted-foreground mb-0.5'>
                      매칭 점수
                    </div>
                    <div className='text-lg font-bold text-primary'>
                      {applicant?.match_score?.total_score?.toFixed(1)}
                    </div>
                  </div>

                  {/* Priority Badge - top 30% are priority */}
                  <div className='w-24'>
                    {applicant?.match_score?.total_score >= 70 ? (
                      <Badge
                        variant='primary'
                        className='w-full justify-center'>
                        우선 검토
                      </Badge>
                    ) : (
                      <Badge variant='ghost' className='w-full justify-center'>
                        일반
                      </Badge>
                    )}
                  </div>

                  {/* Personal Info - Conditional based on blind mode */}
                  {!isBlindMode && (
                    <div className='flex items-center gap-6'>
                      <div className='w-48'>
                        <div className='text-xs text-muted-foreground mb-0.5'>
                          학력
                        </div>
                        <div className='text-sm font-medium text-gray-900'>
                          {applicant?.education || '-'}
                        </div>
                      </div>
                      <div className='w-28'>
                        <div className='text-xs text-muted-foreground mb-0.5'>
                          나이
                        </div>
                        <div className='text-sm font-medium text-gray-900'>
                          {applicant?.age ? `${applicant?.age}세` : '-'}
                        </div>
                      </div>
                      <div className='w-16'>
                        <div className='text-xs text-muted-foreground mb-0.5'>
                          성별
                        </div>
                        <div className='text-sm font-medium text-gray-900'>
                          {applicant?.gender || '-'}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Spacer */}
                  <div className='flex-1' />

                  {/* Evaluation Toggle Button */}
                  <div className='w-32'>
                    <Button
                      variant='ghost'
                      size='sm'
                      onClick={() => toggleCard(applicant?.applicant_id)}
                      className='gap-2 w-full'>
                      {expandedCards.has(applicant?.applicant_id) ? (
                        <div className='flex items-center justify-center gap-2'>
                          심사평 닫기
                          <img src={up} alt='닫기' className='w-3 h-3' />
                        </div>
                      ) : (
                        <div className='flex items-center justify-center gap-2'>
                          심사평 보기
                          <img src={down} alt='닫기' className='w-3 h-3' />
                        </div>
                      )}
                    </Button>
                  </div>
                </div>

                {/* Expanded Evaluation */}
                {expandedCards.has(applicant?.applicant_id) && (
                  <div className='px-4 pb-4'>
                    {console.log('Rendering expanded view for applicant:', applicant)}
                    <div className='bg-gray-50 rounded-lg p-4 border border-gray-200 space-y-4'>
                      {/* Interview Summary */}
                      <div>
                        <h4 className='font-semibold text-sm mb-2 text-gray-900'>
                          심사평
                        </h4>
                        <p className='text-sm text-gray-700 leading-relaxed'>
                          {applicant?.interview_summary}
                        </p>
                      </div>

                      {/* Highlights */}
                      {applicant?.highlights?.length > 0 && (
                        <div>
                          <h4 className='font-semibold text-sm mb-2 text-gray-900'>
                            주요 특징
                          </h4>
                          <div className='flex flex-wrap gap-2'>
                            {applicant?.highlights.map((highlight, idx) => (
                              <div
                                key={idx}
                                variant='secondary'
                                className='text-xs'>
                                {highlight}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Strengths & Weaknesses */}
                      <div className='grid grid-cols-2 gap-4'>
                        {/* Strengths */}
                        {applicant?.match_score?.strengths?.length > 0 && (
                          <div>
                            <h4 className='font-semibold text-sm mb-2 text-green-700'>
                              강점
                            </h4>
                            <ul className='text-sm text-gray-700 space-y-1'>
                              {applicant?.match_score?.strengths.map(
                                (strength, idx) => (
                                  <li
                                    key={idx}
                                    className='flex items-start gap-2'>
                                    <span className='text-green-600 mt-0.5'>
                                      •
                                    </span>
                                    <span>{strength}</span>
                                  </li>
                                )
                              )}
                            </ul>
                          </div>
                        )}

                        {/* Weaknesses */}
                        {applicant?.match_score?.weaknesses?.length > 0 && (
                          <div>
                            <h4 className='font-semibold text-sm mb-2 text-orange-700'>
                              개선점
                            </h4>
                            <ul className='text-sm text-gray-700 space-y-1'>
                              {applicant?.match_score?.weaknesses.map(
                                (weakness, idx) => (
                                  <li
                                    key={idx}
                                    className='flex items-start gap-2'>
                                    <span className='text-orange-600 mt-0.5'>
                                      •
                                    </span>
                                    <span>{weakness}</span>
                                  </li>
                                )
                              )}
                            </ul>
                          </div>
                        )}
                      </div>

                      {/* Detailed Scores */}
                      <div>
                        <h4 className='font-semibold text-sm mb-2 text-gray-900'>
                          세부 점수
                        </h4>
                        <div className='grid grid-cols-2 gap-3 text-sm'>
                          <div className='flex justify-between'>
                            <span className='text-gray-600'>기술 역량</span>
                            <span className='font-medium'>
                              {applicant?.match_score?.technical_score?.toFixed(1)}
                            </span>
                          </div>
                          <div className='flex justify-between'>
                            <span className='text-gray-600'>문화 적합도</span>
                            <span className='font-medium'>
                              {applicant?.match_score?.cultural_score?.toFixed(1)}
                            </span>
                          </div>
                          <div className='flex justify-between'>
                            <span className='text-gray-600'>경험</span>
                            <span className='font-medium'>
                              {applicant?.match_score?.experience_score?.toFixed(
                                1
                              )}
                            </span>
                          </div>
                          <div className='flex justify-between'>
                            <span className='text-gray-600'>소프트 스킬</span>
                            <span className='font-medium'>
                              {applicant?.match_score?.soft_skills_score?.toFixed(
                                1
                              )}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
