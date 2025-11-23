import CameraPreview from './CameraPreview';
import AgentPanel from './AgentPanel';
import InterviewPageLayout from './InterviewPageLayout';
import useAudioStreaming from '@lib/useAudioStreaming';
import {useEffect, useState} from 'react';
import Button from '@components/Button';
import EndButton from './EndButton';
import SideBar from './SideBar';
import InterviewLog from './InterviewLog';
import {useLocation} from 'react-router-dom';
import useInterviewSession from '@lib/useInterviewSession';

const InterviewPage = () => {
  const {state} = useLocation();
  console.log('state:', state);
  const websocketUrl = state?.websocketUrl;
  const interviewId = state?.interviewId;

  const {
    getSocket,
    turnState,
    currentQuestion,
    logs,
    finishAnswerManually,
    TURN_STATE,
    SESSION_STATE,
  } = useInterviewSession({websocketUrl});

  const {
    status: audioStatus,
    startRecording,
    stopRecording,
    rms,
    STATUS,
  } = useAudioStreaming({getSocket, turnState});

  // ANSWERING 상태에서만 자동 녹음 시작
  useEffect(() => {
    const s = getSocket?.();
    console.log('Socket instance:', s);
    console.log('Socket state:', s?.readyState);

    if (turnState === 'answering') {
      startRecording();
    } else {
      stopRecording();
    }
  }, [turnState]);

  return (
    <InterviewPageLayout>
      <SideBar />

      {/* Center Content */}
      <main className='flex flex-1 flex-col p-6'>
        {/* Video Screens Container */}
        <section className='grid flex-1 grid-cols-2 gap-6 items-center *:flex *:flex-col *:gap-4'>
          <AgentPanel />
          <CameraPreview />
        </section>

        <div className='flex-center gap-10'>
          <Button
            variant='outline'
            className='text-white font-bold hover:text-grey'
            onClick={startRecording}>
            소켓 요청
          </Button>
          <Button
            variant='outline'
            className='text-white font-bold hover:text-grey'
            onClick={stopRecording}>
            CLOSE
          </Button>
        </div>

        <EndButton />
      </main>

      <InterviewLog />
    </InterviewPageLayout>
  );
};

export default InterviewPage;
