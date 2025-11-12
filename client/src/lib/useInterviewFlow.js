import {useEffect, useState} from 'react';
import {useSTT} from './useSTT';

const QUESTIONS = [
  '최근 프로젝트에서 맡은 역할을 말씀해주세요.',
  '팀 내 협업 중 가장 도전적이었던 순간은 무엇인가요?',
  '성능 최적화를 위해 수행한 조치를 설명해주세요.',
];

export function useInterviewFlow() {
  const [phase, setPhase] = useState('answering'); // idle | greeting | questioning | answering | processing | done
  const [index, setIndex] = useState(0);
  const [transcript, setTranscript] = useState('');
  const {startSTT, stopSTT, onTranscript, onFinal} = useSTT();

  const currentQuestion = QUESTIONS[index];

  useEffect(() => {
    onTranscript((text) => setTranscript(text));
    onFinal(async (text) => {
      setPhase('processing');
      setTranscript('');

      // send to backend
      await fetch('/api/interview/answer', {
        method: 'post',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({question: currentQuestion, answer: text}),
      });

      if (index + 1 < QUESTIONS.length) {
        setIndex((i) => i + 1);
        setPhase('questioning');
      } else {
        setPhase('done');
      }
    });
  }, [index]);

  const startInterview = () => {
    setPhase('greeting');
  };

  return {phase, currentQuestion, transcript, startInterview, index};
}
