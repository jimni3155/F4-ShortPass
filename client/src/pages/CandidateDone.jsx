import Button from '../components/Button';
import {useNavigate} from 'react-router-dom';

const CandidateDone = () => {
  const navigate = useNavigate();
  const candidateId = 'candidate-123';
  const companyScores = [
    {company: '테크 스타트업 A', matchingScore: 92},
    {company: '글로벌 기업 B', matchingScore: 85},
    {company: '핀테크 회사 C', matchingScore: 78},
  ];

  return (
    <div className='w-full min-h-screen flex justify-center items-center'>
      <div className='md:w-1/2 flex flex-col gap-10'>
        <div className='flex flex-col items-center space-y-5 text-center'>
          <h1 className='text-4xl md:text-6xl font-bold text-dark'>
            면접이 종료되었습니다
          </h1>
          <p className='text-base md:text-lg leading-relaxed text-grey'>
            귀한 시간 내어 참여해 주셔서 감사합니다
          </p>
        </div>

        {/* 회사별 매칭 점수 */}
        <div className='w-full space-y-5'>
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
