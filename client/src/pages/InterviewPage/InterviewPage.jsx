import CameraPreview from './CameraPreview';
import AgentPanel from './AgentPanel';
import InterviewPageLayout from './InterviewPageLayout';
import useAudioStreaming from '@lib/useAudioStreaming';
import QuestionPanel from './QuestionPanel';
import {useInterviewFlow} from '@lib/useInterviewFlow';
import {useEffect} from 'react';
import Button from '@components/Button';
import EndButton from './EndButton';

const InterviewPage = () => {
  // const {phase, currentQuestion, transcript, startInterview, index} =
  //   useInterviewFlow();

  // useEffect(() => {
  //   startInterview();
  // }, []);

  // return (
  //   <InterviewPageLayout>
  //     <QuestionPanel
  //       phase={phase}
  //       currentQuestion={currentQuestion}
  //       currentQuestionIndex={index + 1}
  //     />
  //     <section className='w-full flex my-auto gap-10'>
  //       <AgentPanel />
  //       <CameraPreview />
  //     </section>

  //     {phase === 'done' && <EndButton />}
  //   </InterviewPageLayout>
  // );
  const {status, rms, startRecording, stopRecording, STATUS} =
    useAudioStreaming();

  const isBusy = status === STATUS.RECORDING || status === STATUS.PREPARING;
  const currentQuestion = '최근 프로젝트에서 맡은 역할을 말씀해주세요.';
  const index = 0;
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);

  const QUESTIONS = [
    '최근 프로젝트에서 맡은 역할을 말씀해주세요.',
    '팀 내 협업 중 가장 도전적이었던 순간은 무엇인가요?',
    '성능 최적화를 위해 수행한 조치를 설명해주세요.',
    '최근 프로젝트에서 맡은 역할을 말씀해주세요.',
    '팀 내 협업 중 가장 도전적이었던 순간은 무엇인가요?',
    '성능 최적화를 위해 수행한 조치를 설명해주세요.',
    '최근 프로젝트에서 맡은 역할을 말씀해주세요.',
    '팀 내 협업 중 가장 도전적이었던 순간은 무엇인가요?',
    '성능 최적화를 위해 수행한 조치를 설명해주세요.',
  ];

  return (
    <InterviewPageLayout>
      {/* <SideBar /> */}

      {/* Center Content */}
      <main className='flex flex-1 flex-col p-6'>
        {/* Video Screens Container */}
        <section className='grid flex-1 grid-cols-2 gap-6 items-center *:flex *:flex-col *:gap-4'>
          <AgentPanel />
          <CameraPreview />
        </section>
        <button
          className='text-white font-bold border border-white'
          onClick={startRecording}>
          소켓 요청
        </button>
        <button
          className='text-white font-bold border border-white'
          onClick={stopRecording}>
          CLOSE
        </button>
        {/* <QuestionBar /> */}
      </main>

      {/* <InterviewLog /> */}
    </InterviewPageLayout>
  );
};

export default InterviewPage;
