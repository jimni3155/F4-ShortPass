import {useState} from 'react';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  Radar,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';
import {useNavigate, useParams} from 'react-router-dom';
import Button from '@components/Button';
import Badge from '@components/Badge';
import download from '@assets/svg/download.svg';
import ChevronDown from '@assets/svg/chevron-down.svg';
import ChevronUp from '@assets/svg/chevron-up.svg';
import applicantA from '@mock/applicantA'
import applicantB from '@mock/applicantB'
import bookmarkActive from '@assets/svg/bookmark-blue.svg'
import bookmark from '@assets/svg/bookmark.svg'

export default function CandidateEvaluation() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('common');
  const [expandedCompetencies, setExpandedCompetencies] = useState({});
  const [bookmarked, setBookmarked] = useState(false);

  // 메모 State 추가
  const [memo, setMemo] = useState('');

  const applicantData = (id === '1') ? applicantA : applicantB;
  if (!applicantData) return null;

  const {applicant, score_breakdown, overall_summary, competency_scores, competency_details, recommendedQuestions, keywords, transcript} = applicantData

  const toggleCompetency = (competency) => {
    setExpandedCompetencies((prev) => ({
      ...prev,
      [competency]: !prev[competency],
    }));
  };

  const handleSaveMemo = () => {
    // 여기에 API 저장 로직 구현
    alert('메모가 저장되었습니다.');
    console.log("Saved Memo:", memo);
  };

  const commonChartData = score_breakdown.common_competencies.map(
    (key) => ({
      subject: key,
      score: competency_scores[key],
      fullMark: 100,
    })
  );

  const jobChartData = score_breakdown.job_competencies.map(
    (key) => ({
      subject: key,
      score: competency_scores[key],
      fullMark: 100,
    })
  );

  const CustomTooltip = ({active, payload}) => {
    if (active && payload && payload.length) {
      return (
        <div className='bg-white px-3 py-2 border border-gray-200 rounded shadow-sm'>
          <p className='text-sm font-medium text-gray-900'>
            {payload[0].payload.subject}
          </p>
          <p className='text-sm text-blue-600'>{payload[0].value}%</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className='min-h-screen'>
      {/* 메인 */}
      <div className='flex-1 overflow-y-auto'>
        {/* 헤더 */}
        <div className='border-b border-gray-200'>
          <div className='max-w-7xl mx-auto px-8 py-6'>
            <button
              onClick={() => navigate('/company/result')}
              className='text-sm text-gray-600 hover:text-gray-900 mb-4'>
              ← 목록으로 돌아가기
            </button>
            <div className='flex items-center justify-between'>
              <div>
                <h1 className='text-2xl font-semibold text-blue'>
                  지원자 인사이트
                </h1>
              </div>
            </div>
          </div>
        </div>

        {/* Content Area */}
        <div className='max-w-7xl mx-auto px-8 py-8'>
          {/* 지원자 정보 */}
          <div className='mb-8 pb-8 border-b border-gray-200'>
            <div className='flex items-center justify-between'>
              <h2 className='text-lg font-semibold text-gray-900 mb-4'>
                지원자 정보
              </h2>
              <button className='cursor-pointer' onClick={() => setBookmarked(!bookmarked)}>
                {bookmarked ? <img src={bookmarkActive} alt='북마크' className='w-6 h-6' /> : <img src={bookmark} alt='북마크' className='w-6 h-6'/>}
              </button>
            </div>

            <div className='grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-x-8 gap-y-4'>
              <div>
                <div className='text-sm text-gray-600 mb-1'>이름</div>
                <div className='text-base font-medium text-gray-900'>
                  {applicant.name}
                </div>
              </div>
              <div>
                <div className='text-sm text-gray-600 mb-1'>나이</div>
                <div className='text-base font-medium text-gray-900'>
                  {applicant.age}세
                </div>
              </div>
              <div>
                <div className='text-sm text-gray-600 mb-1'>성별</div>
                <div className='text-base font-medium text-gray-900'>
                  {applicant.gender}
                </div>
              </div>
              <div>
                <div className='text-sm text-gray-600 mb-1'>이메일</div>
                <div className='text-base font-medium text-gray-900'>
                  {applicant.email}
                </div>
              </div>
              <div>
                <div className='text-sm text-gray-600 mb-1'>학교</div>
                <div className='text-base font-medium text-gray-900'>
                  {applicant.school}
                </div>
              </div>
              <div>
                <div className='text-sm text-gray-600 mb-1'>전공</div>
                <div className='text-base font-medium text-gray-900'>
                  {applicant.major}
                </div>
              </div>
              <div>
                <div className='text-sm text-gray-600 mb-1'>학점</div>
                <div className='text-base font-medium text-gray-900'>
                  {applicant.gpa.toFixed(2)} / 4.5
                </div>
              </div>
              <div>
                <div className='text-sm text-gray-600 mb-1'>지원 직무</div>
                <div className='text-base font-medium text-gray-900'>
                  {applicant.position}
                </div>
              </div>
              <div>
                <div className='text-sm text-gray-600 mb-1'>최종 점수</div>
                <div className='text-base font-semibold text-blue'>
                  {score_breakdown.final_score}%
                </div>
              </div>
              <div>
                <div className='text-sm text-gray-600 mb-1'>직무 역량 점수</div>
                <div className='text-base font-semibold text-[#50C878]'>
                  {score_breakdown.job_score}%
                </div>
              </div>
              <div>
                <div className='text-sm text-gray-600 mb-1'>공통 역량 점수</div>
                <div className='text-base font-semibold text-[#FFA500]'>
                  {score_breakdown.common_score}%
                </div>
              </div>
              <div>
                <div className='text-sm text-gray-600 mb-1'>주목 인재 여부</div>
                <div className='text-base font-medium text-gray-900'>
                  {true && (
                    <Badge variant='secondary'>주목 인재</Badge>
                  )}
                </div>
              </div>
            </div>
            <div className='mt-6 flex justify-end'>
              <Button variant='primary' className='flex-center gap-2 text-sm'>
                <img src={download} alt='이력서 다운로드' className='w-4 h-4' />
                이력서 다운로드
              </Button>
            </div>
          </div>

          {/* AI Analysis Section */}
          <div className='mb-8 pb-8 border-b border-gray-200'>
            <h2 className='text-lg mb-4 font-semibold text-gray-900'>
              AI 심층 분석 심사평
            </h2>
            <p className='text-sm text-gray-700 leading-relaxed whitespace-pre-line'>
              {overall_summary.overall_evaluation_summary}
            </p>
          </div>

          <div className='mb-8 pb-8 border-b border-gray-200'>
            <div className='grid grid-cols-1 lg:grid-cols-3 gap-6'>
              {/* 공통 & 직무 역량  */}
              <div className='lg:col-span-2 border border-gray-200 rounded-lg bg-white p-6'>
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
                      <div className='absolute bottom-0 left-0 right-0 h-0.5 rounded-full bg-gray-900' />
                    )}
                  </button>
                </div>

                {activeTab === 'common' && (
                  <div>
                    <div className='mb-4'>
                      <h3 className='text-lg font-semibold text-gray-900 mb-1'>
                        공통역량 평가
                      </h3>
                      <p className='text-sm text-gray-600'>
                        AI가 면접 답변 기반으로 산출한 5개 영역 역량 점수입니다.
                      </p>
                    </div>

                    <ResponsiveContainer width='100%' height={400}>
                      <RadarChart data={commonChartData}>
                        <PolarGrid stroke='#e5e7eb' />
                        <PolarAngleAxis
                          dataKey='subject'
                          tick={{fill: '#4b5563', fontSize: 13}}
                        />
                        <Tooltip content={<CustomTooltip />} />
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

                    <div className='mt-6 space-y-2'>
                      {score_breakdown.common_competencies.map(
                        (key, index) => (
                          <div
                            key={key}
                            className='border-b border-gray-100 pb-2'>
                            <div className='flex items-center justify-between'>
                              <span className='text-sm text-gray-700 font-medium'>
                                {key}
                              </span>
                              <div className='flex items-center gap-3'>
                                <div className='w-32 bg-gray-200 rounded-full h-2'>
                                  <div
                                    className='bg-pink-500 h-2 rounded-full'
                                    style={{width: `${competency_scores[key]}%`}}
                                  />
                                </div>
                                <span className='font-medium text-sm text-gray-900 w-12 text-right'>
                                  {competency_scores[key]}%
                                </span>
                                <button
                                  onClick={() => toggleCompetency(key)}
                                  className='p-1 hover:bg-gray-100 rounded'>
                                  {expandedCompetencies[key] ? (
                                    <img
                                      src={ChevronUp}
                                      alt='열기'
                                      className='w-4 h-4'
                                    />
                                  ) : (
                                    <img
                                      src={ChevronDown}
                                      alt='닫기'
                                      className='w-4 h-4'
                                    />
                                  )}
                                </button>
                              </div>
                            </div>
                            {expandedCompetencies[key] && (
                              <div className='mt-2 pl-4 text-sm text-gray-600 leading-relaxed'>
                              <p>{competency_details[key].connected_summary}</p>
                              <ul className='mt-4'>
                                <p className='font-medium'>강점</p>
                                {competency_details[key].strengths.map((strength, index) => (
                                  <li key={`strength-${index}`}>
                                    <span className='text-blue-600 font-medium'>
                                      {index + 1}{'. '}
                                    </span>
                                    <span>{strength}</span>
                                  </li>
                                ))}
                              </ul>
                              <ul className='mt-4'>
                              <p className='font-medium'>약점</p>
                                {competency_details[key].weaknesses.map((weakness, index) => (
                                  <li key={`weakness-${index}`}>
                                    <span className='text-blue-600 font-medium'>
                                      {index + 1}{'. '}
                                    </span>
                                    <span>{weakness}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                            )}
                          </div>
                        )
                      )}
                    </div>
                  </div>
                )} 

                {activeTab === 'job' && (
                  <div>
                    <div className='mb-4'>
                      <h3 className='text-lg font-semibold text-gray-900 mb-1'>
                        직무역량 평가
                      </h3>
                      <p className='text-sm text-gray-600'>
                        JD 기반 직무 관련 5가지 핵심 역량 평가 결과입니다.
                      </p>
                    </div>

                    <ResponsiveContainer width='100%' height={400}>
                      <RadarChart data={jobChartData}>
                        <PolarGrid stroke='#e5e7eb' />
                        <PolarAngleAxis
                          dataKey='subject'
                          tick={{fill: '#4b5563', fontSize: 13}}
                        />
                        <Tooltip content={<CustomTooltip />} />
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

                    <div className='mt-6 space-y-2'>
                      {score_breakdown.job_competencies.map(
                        (key, index) => (
                          <div
                            key={key}
                            className='border-b border-gray-100 pb-2'>
                            <div className='flex items-center justify-between'>
                              <span className='text-sm text-gray-700 font-medium'>
                                {key}
                              </span>
                              <div className='flex items-center gap-3'>
                                <div className='w-32 bg-gray-200 rounded-full h-2'>
                                  <div
                                    className='bg-cyan-500 h-2 rounded-full'
                                    style={{width: `${competency_scores[key]}%`}}
                                  />
                                </div>
                                <span className='font-medium text-sm text-gray-900 w-12 text-right'>
                                {competency_scores[key]}%
                                </span>
                                <button
                                  onClick={() => toggleCompetency(key)}
                                  className='p-1 hover:bg-gray-100 rounded'>
                                  {expandedCompetencies[key] ? (
                                    <img
                                      src={ChevronUp}
                                      alt='열기'
                                      className='w-4 h-4'
                                    />
                                  ) : (
                                    <img
                                      src={ChevronDown}
                                      alt='닫기'
                                      className='w-4 h-4'
                                    />
                                  )}
                                </button>
                              </div>
                            </div>
                            {expandedCompetencies[key] && (
                              <div className='mt-2 pl-4 text-sm text-gray-600 leading-relaxed'>
                                <p>{competency_details[key].connected_summary}</p>
                                <ul className='mt-4'>
                                  <p className='font-medium'>강점</p>
                                  {competency_details[key].strengths.map((strength, index) => (
                                    <li key={`strength-${index}`}>
                                      <span className='text-blue-600 font-medium'>
                                        {index + 1}{'. '}
                                      </span>
                                      <span>{strength}</span>
                                    </li>
                                  ))}
                                </ul>
                                <ul className='mt-4'>
                                <p className='font-medium'>약점</p>
                                  {competency_details[key].weaknesses.map((weakness, index) => (
                                    <li key={`weakness-${index}`}>
                                      <span className='text-blue-600 font-medium'>
                                        {index + 1}{'. '}
                                      </span>
                                      <span>{weakness}</span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                        )
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* 인터뷰 transcript */}
              <div className='lg:col-span-1'>
                <div className='border border-gray-200 rounded-lg bg-white overflow-hidden h-full'>
                  <div className='bg-gray-50 border-b border-gray-200 px-4 py-3'>
                    <h3 className='text-sm font-semibold text-gray-900'>
                      면접 Transcript
                    </h3>
                    <p className='text-xs text-gray-600 mt-0.5'>
                      전체 질문-답변 기록
                    </p>
                  </div>
                  <div className='px-4 py-4 space-y-3 max-h-[710px] overflow-y-auto'>
                    {transcript.map((item, index) => (
                      <div
                        key={index}
                        className='pb-3 border-b border-gray-100 last:border-0'>
                        <div className='flex items-center gap-2 mb-1.5'>
                          <span
                            className={`text-xs font-medium px-2 py-0.5 rounded ${
                              item.type === 'question'
                                ? 'bg-purple-100 text-purple-700'
                                : 'bg-green-100 text-green-700'
                            }`}>
                            {item.type === 'question' ? `Q` : 'A'}
                          </span>
                        </div>
                        <p className='text-xs text-gray-700 leading-relaxed'>
                          {item.text}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* 요약 평가 키워드 + 추천 질문 */}
          <div className='mb-8 pb-8 border-b border-gray-200'>
            <h2 className='text-lg font-semibold text-gray-900 mb-4'>
              요약 평가 키워드
            </h2>

            <div className='mb-4'>
              <div className='text-sm text-gray-600 mb-2'>긍정</div>
              <div className='flex flex-wrap gap-2'>
                {keywords.positive.map((keyword, index) => (
                  <span
                    key={index}
                    className='px-3 py-1.5 bg-green-50 text-green-600 text-sm rounded-xl border-[0.5px] border-green-400 '>
                    {keyword}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <div className='text-sm text-gray-600 mb-2'>부정</div>
              <div className='flex flex-wrap gap-2'>
                {keywords.negative.map((keyword, index) => (
                  <span
                    key={index}
                    className='px-3 py-1.5 bg-red-50 text-red-600 text-sm rounded-xl border-[0.5px] border-red-400'>
                    {keyword}
                  </span>
                ))}
              </div>
            </div>
          </div>

          <div className='mb-8 pb-8 border-b border-gray-200'>
            <h2 className='text-lg font-semibold text-gray-900 mb-4'>
              추천 질문 목록
            </h2>
            <p className='text-sm text-gray-600 mb-4'>
              지원자의 답변을 바탕으로 AI가 생성한 심화 면접 질문입니다.
            </p>
            <ul className='space-y-3'>
              {recommendedQuestions.map((question, index) => (
                <li key={index} className='flex gap-3 text-sm text-gray-700'>
                  <span className='text-blue-600 font-medium'>
                    {index + 1}.
                  </span>
                  <span>{question}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* 면접관 메모 (추가됨) */}
          <div className='mb-8'>
            <h2 className='text-lg font-semibold text-gray-900 mb-4'>
              HR 메모
            </h2>
            <div className='bg-white rounded-lg'>
              <textarea
                value={memo}
                onChange={(e) => setMemo(e.target.value)}
                placeholder='지원자에 대한 특이사항이나 의견을 작성해주세요.'
                className='w-full h-32 p-4 border border-gray-200 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:outline-none text-sm text-gray-900 placeholder-gray-400'
              />
              <div className='mt-3 flex justify-end'>
                <Button 
                  variant='primary' 
                  className='text-sm px-6'
                  onClick={handleSaveMemo}
                >
                  저장
                </Button>
              </div>
            </div>
          </div>

        </div> 
      </div>
    </div>
  );
}