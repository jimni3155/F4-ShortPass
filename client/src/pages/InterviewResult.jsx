import Badge from '@components/Badge';
import {COMPANY_RESULTS} from '@mock/CompanyMatchingResults';

const InterviewResult = () => {
  const result = COMPANY_RESULTS;

  const averageScore =
    result?.applicants.length > 0
      ? (
          result.applicants.reduce((sum, a) => sum + a.total_score, 0) /
          result.applicants.length
        ).toFixed(1)
      : 0;

  return (
    <div className='min-h-screen bg-white'>
      <div className='container mx-auto px-8 py-12 max-w-[1400px]'>
        <h1 className='text-3xl font-bold text-blue mb-8'>
          AI가 분석한 지원자별 역량과 평가 결과를 한눈에 확인하세요.
        </h1>

        <div className='mb-8'>
          <div className='grid grid-cols-3 gap-x-12 gap-y-6'>
            <div>
              <div className='text-xs text-gray-500 mb-2'>기업명</div>
              <div className='text-base font-medium text-gray-900'>
                {result?.company_name}
              </div>
            </div>
            <div>
              <div className='text-xs text-gray-500 mb-2'>채용 공고명</div>
              <div className='text-base font-medium text-gray-900'>
                {result?.job_title}
              </div>
            </div>
            <div>
              <div className='text-xs text-gray-500 mb-2'>채용 부서</div>
              <div className='text-base font-medium text-gray-900'>
                {result?.department}
              </div>
            </div>
            <div>
              <div className='text-xs text-gray-500 mb-2'>진행 기간</div>
              <div className='text-base font-medium text-gray-900'>
                {result?.recruitment_period}
              </div>
            </div>
            <div>
              <div className='text-xs text-gray-500 mb-2'>지원 현황</div>
              <div className='text-base font-medium text-gray-900'>
                지원자 <span>{result?.total_applicants}</span>명 중{' '}
                <span className=''>{result?.completed_evaluations}</span>명 평가
                완료
              </div>
            </div>
            <div>
              <div className='text-xs text-gray-500 mb-2'>평균 평가 점수</div>
              <div className='text-base font-medium text-gray-900'>
                {averageScore}점
              </div>
            </div>
          </div>
        </div>

        <div className='mb-6'>
          {/* <div className='flex gap-3 items-center'>
            <Select value={trackFilter} onValueChange={setTrackFilter}>
              <SelectTrigger className='w-[180px] border-gray-300'>
                <SelectValue placeholder='트랙 선택' />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value='all'>전체 트랙</SelectItem>
                <SelectItem value='전략'>전략</SelectItem>
                <SelectItem value='운영'>운영</SelectItem>
                <SelectItem value='디지털'>디지털</SelectItem>
              </SelectContent>
            </Select>
            <Select value={priorityFilter} onValueChange={setPriorityFilter}>
              <SelectTrigger className='w-[180px] border-gray-300'>
                <SelectValue placeholder='검토 상태' />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value='all'>전체</SelectItem>
                <SelectItem value='priority'>우선 검토</SelectItem>
                <SelectItem value='normal'>일반</SelectItem>
              </SelectContent>
            </Select>
          </div> */}
        </div>

        <div className='bg-white rounded-md border border-gray-200 overflow-hidden'>
          <div className='grid grid-cols-11 gap-4 px-6 py-3 bg-gray-50 border-b border-gray-200 text-xs font-medium text-gray-600'>
            <div className='col-span-1'>지원자명</div>
            <div className='col-span-1'>지원 분야</div>
            <div className='col-span-1'>인터뷰 일자</div>
            <div className='col-span-1 text-center'>최종 점수</div>
            <div className='col-span-1'>주요 강점</div>
            <div className='col-span-1'>개선 필요점</div>
            <div className='col-span-4'>AI 종합 의견</div>
            <div className='col-span-1 text-center'>검토 상태</div>
          </div>

          <div>
            {result?.applicants?.map((applicant, idx) => (
              <div
                key={applicant.applicant_id}
                className={`grid grid-cols-11 gap-4 px-6 py-4 border-b border-gray-100 hover:bg-gray-50 transition-colors `}>
                <div className='col-span-1 flex items-center'>
                  <span className='text-sm font-medium text-gray-900'>
                    {applicant.applicant_name}
                  </span>
                </div>
                <div className='col-span-1 flex items-center'>
                  <span className='text-sm text-gray-700'>
                    {applicant.track}
                  </span>
                </div>
                <div className='col-span-1 flex items-center'>
                  <span className='text-sm text-gray-700'>
                    {applicant.interview_date}
                  </span>
                </div>
                <div className='col-span-1 flex items-center justify-center'>
                  <span className='text-sm font-bold text-blue'>
                    {applicant.total_score}
                  </span>
                </div>
                <div className='col-span-1 flex items-center'>
                  <span className='text-sm text-gray-700'>
                    {applicant.strengths}
                  </span>
                </div>
                <div className='col-span-1 flex items-center'>
                  <span className='text-sm text-gray-700'>
                    {applicant.weaknesses}
                  </span>
                </div>
                <div className='col-span-4 flex items-center'>
                  <span className='text-sm text-gray-700 leading-relaxed'>
                    {applicant.ai_comment}
                  </span>
                </div>
                <div className='col-span-1 flex items-center justify-center'>
                  {applicant.priority_review ? (
                    <Badge
                      classname='px-3 py-1.5 font-medium text-xs rounded-lg'
                      variant='secondary'>
                      우선 검토
                    </Badge>
                  ) : (
                    <Badge classname='text-xs border-gray-300 text-gray-600 w-20 justify-center'>
                      일반
                    </Badge>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default InterviewResult;
