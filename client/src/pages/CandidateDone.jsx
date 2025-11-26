import Button from '../components/Button';
import {useLocation, useNavigate} from 'react-router-dom';

const CandidateDone = () => {
  const navigate = useNavigate();
  const {state} = useLocation();
  const interviewResults = state?.interviewResults || [];
  const personaInfo = state?.personaInfo;
  const transcriptUrl = state?.transcriptUrl;
  const interviewId = state?.interviewId;

  return (
    <div className='w-full min-h-screen flex justify-center items-center'>
      <div className='md:w-1/2 flex flex-col gap-10'>
        <div className='flex flex-col items-center space-y-5 text-center'>
          <h1 className='text-4xl md:text-5xl font-bold text-blue'>
            면접이 종료되었습니다
          </h1>
          <p className='text-base md:text-lg leading-relaxed text-grey'>
            귀한 시간 내어 참여해 주셔서 감사합니다
          </p>
        </div>

        {/* 회사별 매칭 점수 */}
        {/* <div className='w-full space-y-5'>
          <h2 className='text-center text-lg md:text-xl font-semibold text-dark'>
            회사별 매칭 점수
          </h2>
          <div className='space-y-3'>
            {companyScores.map((score) => {
              return (
                <div
                  key={score.company}
                  className='flex items-center justify-between rounded-2xl border border-gray-200 bg-transparent px-6 py-4 backdrop-blur-sm'>
                  <span className='font-medium'>{score.company}</span>
                  <span className='font-semibold text-primary text-right'>
                    {score.matchingScore}%
                  </span>
                </div>
              );
            })}
          </div>
        </div> */}

        {/* 인터뷰 결과 요약 */}
        <div className='w-full space-y-3 rounded-2xl border border-gray-200 px-6 py-5'>
          <div className='flex flex-wrap items-center justify-between gap-2'>
            <h3 className='text-lg font-semibold text-dark'>
              인터뷰 결과 요약 {interviewId ? `(#${interviewId})` : ''}
            </h3>
            {transcriptUrl && (
              <Button
                variant='outline'
                className='text-sm'
                onClick={() => window.open(transcriptUrl, '_blank')}>
                녹취/결과 파일 열기
              </Button>
            )}
          </div>
          {personaInfo?.name && (
            <p className='text-sm text-grey'>
              면접관 페르소나: {personaInfo.name} ({personaInfo.identity})
            </p>
          )}
          {interviewResults.length > 0 ? (
            <div className='space-y-3 max-h-64 overflow-y-auto pr-1'>
              {interviewResults.map((item, idx) => (
                <div
                  key={`${item.question_index}-${idx}`}
                  className='rounded-xl border border-gray-100 bg-gray-50 px-4 py-3'>
                  <div className='text-xs font-semibold text-primary mb-1'>
                    질문 {item.question_index + 1}
                  </div>
                  <div className='text-sm font-medium text-dark'>
                    Q. {item.question}
                  </div>
                  <div className='text-sm text-gray-700 mt-1'>
                    A. {item.answer}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className='text-sm text-grey'>
              아직 인터뷰 결과 데이터가 없습니다. 면접을 완료하면 자동으로
              표시됩니다.
            </p>
          )}
        </div>

        {/* Return home button */}
        <div className='flex justify-center'>
          <Button
            asChild
            onClick={() => {
              navigate('/');
            }}
            variant='primary'
            className='w-fit p-3 px-7'
          >
            홈으로 돌아가기
          </Button>
        </div>
      </div>
    </div>
  );
};

export default CandidateDone;
