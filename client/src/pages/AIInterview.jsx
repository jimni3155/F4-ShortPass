import {useState, useRef, useEffect, useCallback} from 'react';
import {useNavigate} from 'react-router-dom';
import Button from '../components/Button';
import mic from '../assets/svg/mic.svg';
import ConfirmModal from '../components/ConfirmModal';
import API_V1, { getWebSocketURL } from '../lib/apiConfig';

// ---------------------- PCM 변환 헬퍼 함수----------------------
// Float32Array를 16-bit Signed Integer (PCM) ArrayBuffer로 변환하고 Blob으로 만드는 함수
const encodeToPCM = (audioBuffer) => {
  const pcmData = audioBuffer.getChannelData(0); // 모노 채널 1개만 사용 가정
  const buffer = new ArrayBuffer(pcmData.length * 2);
  const view = new DataView(buffer);

  let offset = 0;
  for (let i = 0; i < pcmData.length; i++, offset += 2) {
    const s = Math.max(-1, Math.min(1, pcmData[i]));
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true);
  }
  // 백엔드에서 Raw PCM을 요구하므로 'audio/pcm' 타입으로 Blob을 반환
  return new Blob([buffer], {type: 'audio/pcm'});
};

// ---------------------- 서버 통신을 위한 상수 ----------------------
const MAX_QUESTION_COUNT = 6; // 서버에서 제공할 최대 질문 수 (면접 종료 조건)

const AIInterview = () => {
  const navigate = useNavigate();
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [currentQuestionText, setCurrentQuestionText] =
    useState('면접을 시작합니다...'); // 질문 텍스트
  const [answer, setAnswer] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [isInterviewActive, setIsInterviewActive] = useState(false); // 면접 진행 여부
  const [interviewId, setInterviewId] = useState(null); // 면접 세션 ID

  // Web Audio API 및 PCM 녹음 상태 (이전과 동일)
  const [recordedPcmBlob, setRecordedPcmBlob] = useState(null);
  const audioContextRef = useRef(null);
  const audioChunksRef = useRef([]);
  const inputPointRef = useRef(null);
  const processorRef = useRef(null);
  const currentStreamRef = useRef(null);

  // Audio 재생 참조
  const audioRef = useRef(null);
  const [currentAudioUrl, setCurrentAudioUrl] = useState(null); // 서버에서 받은 질문 오디오 URL
  const audioChunksBufferRef = useRef([]); // TTS 오디오 청크를 받기 위한 버퍼

  // 웹 소켓 참조
  const wsRef = useRef(null);
  const isLastQuestion = currentQuestionIndex === MAX_QUESTION_COUNT; // 질문 수 기준으로 종료

  // ---------------------- 웹 소켓 핸들링 ----------------------

  // 웹 소켓 메시지 수신 처리
  const handleWebSocketMessage = useCallback(
    (event) => {
      // 서버에서 받은 데이터는 ArrayBuffer 또는 Blob일 수 있으므로 이를 처리해야 함
      if (event.data instanceof Blob) {
        // 바이너리 오디오 청크 수신 (TTS)
        audioChunksBufferRef.current.push(event.data);
        console.log('TTS 오디오 청크 수신:', event.data.size, 'bytes');
      } else if (typeof event.data === 'string') {
        // 텍스트 메시지 수신
        try {
          const message = JSON.parse(event.data);
          console.log('WebSocket 메시지 수신:', message);

          if (message.type === 'question_start') {
            // 질문 시작 - 텍스트 표시 및 오디오 청크 버퍼 초기화
            setCurrentQuestionText(message.text);
            audioChunksBufferRef.current = [];
            setIsSubmitting(false); // 새 질문을 받았으므로 제출 상태 해제
            console.log('질문 시작:', message.text);
          } else if (message.type === 'question_end') {
            // 질문 오디오 전송 완료 - 모든 청크를 합쳐서 재생
            console.log('질문 오디오 전송 완료. 총', audioChunksBufferRef.current.length, '개 청크');

            // 이전 오디오 URL 해제
            if (currentAudioUrl) {
              URL.revokeObjectURL(currentAudioUrl);
            }

            // 모든 청크를 하나의 Blob으로 합치기
            const audioBlob = new Blob(audioChunksBufferRef.current, { type: 'audio/mpeg' });
            const url = URL.createObjectURL(audioBlob);
            setCurrentAudioUrl(url);

            // 오디오 재생
            if (audioRef.current) {
              audioRef.current.onloadeddata = () => {
                audioRef.current.play();
                console.log('질문 오디오 재생 시작');
              };
              audioRef.current.onended = () => {
                setIsInterviewActive(true); // 오디오 재생 완료 후 답변 가능
                console.log('질문 오디오 재생 완료');
              };
              audioRef.current.load();
            }
          } else if (message.type === 'answer_text') {
            // STT 변환된 답변 텍스트
            console.log('STT 변환 완료:', message.text);
            setAnswer(message.text);
          } else if (message.type === 'generating_question') {
            // 다음 질문 생성 중
            console.log('다음 질문 생성 중...');
            setIsSubmitting(true);
          } else if (message.type === 'transcribing_start') {
            // STT 변환 시작
            console.log('음성을 텍스트로 변환 중...');
          } else if (message.type === 'interview_done') {
            // 면접 종료
            console.log('면접 종료:', message.message);
            setShowConfirmModal(true);
            setIsInterviewActive(false);
          } else if (message.type === 'error') {
            // 에러 발생
            console.error('서버 에러:', message.message);
            alert('오류: ' + message.message);
          }
        } catch (e) {
          console.error('수신된 텍스트 메시지 파싱 오류:', e);
        }
      }
    },
    [currentAudioUrl]
  );

  // 면접 준비 및 웹 소켓 연결
  useEffect(() => {
    const initializeInterview = async () => {
      try {
        // 1. 면접 세션 준비 (테스트용 데이터 사용)
        // 실제로는 이전 페이지에서 candidateId와 companyIds를 받아와야 함
        const prepareResponse = await fetch(`${API_V1}/interviews/prepare`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            candidateId: '1', // 테스트용 지원자 ID
            companyIds: ['1', '2'], // 테스트용 회사 ID 목록
          }),
        });

        if (!prepareResponse.ok) {
          throw new Error('면접 준비 실패');
        }

        const { interviewId: newInterviewId } = await prepareResponse.json();
        setInterviewId(newInterviewId);
        console.log('면접 세션 준비 완료. Interview ID:', newInterviewId);

        // 2. WebSocket 연결 (Mock: applicant_id=101 김지원 이력서 기반 질문)
        const wsUrl = getWebSocketURL(`/api/v1/ws/interview/${newInterviewId}?applicant_id=101`);
        console.log('WebSocket 연결 시도:', wsUrl);
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
          console.log('WebSocket 연결 성공');
        };

        ws.onmessage = handleWebSocketMessage;

        ws.onerror = (error) => {
          console.error('WebSocket 오류 발생:', error);
          alert('서버 연결에 문제가 발생했습니다.');
        };

        ws.onclose = () => {
          console.log('WebSocket 연결 종료');
        };

      } catch (error) {
        console.error('면접 초기화 오류:', error);
        alert('면접을 시작할 수 없습니다: ' + error.message);
      }
    };

    initializeInterview();

    // 컴포넌트 언마운트 시 연결 종료
    return () => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.close();
      }
      // 메모리 누수를 막기 위해 Blob URL 해제
      if (currentAudioUrl) {
        URL.revokeObjectURL(currentAudioUrl);
      }
    };
  }, []); // 빈 의존성 배열로 마운트 시 한 번만 실행

  const startRecording = async () => {
    try {
      audioChunksRef.current = []; // 새 녹음 시작 시 청크 초기화
      setRecordedPcmBlob(null);

      const stream = await navigator.mediaDevices.getUserMedia({audio: true});
      currentStreamRef.current = stream; // 스트림 저장

      const audioContext = new (window.AudioContext ||
        window.webkitAudioContext)();
      audioContextRef.current = audioContext;

      // ************* 대체 로직 시작 *************

      // 1. AudioWorklet 모듈 등록 (최초 1회 필요)
      await audioContext.audioWorklet.addModule('/audio-processor.js');

      // 2. AudioWorkletNode 생성
      // 'recorder-processor'는 audio-processor.js에 등록된 이름입니다.
      const recorderNode = new AudioWorkletNode(
        audioContext,
        'recorder-processor',
        {
          numberOfInputs: 1,
          numberOfOutputs: 0, // 출력을 사용하지 않으므로 0
          channelCount: 1, // 모노로 설정
        }
      );
      processorRef.current = recorderNode;

      // 3. AudioWorkletNode에서 메시지 수신 (오디오 데이터)
      recorderNode.port.onmessage = (event) => {
        // 수신된 ArrayBuffer를 Float32Array로 변환하여 청크에 저장
        const float32Array = new Float32Array(event.data);
        audioChunksRef.current.push(float32Array);
      };

      // 4. 노드 연결: Source -> RecorderNode
      const inputPoint = audioContext.createMediaStreamSource(stream);
      inputPointRef.current = inputPoint;

      inputPoint.connect(recorderNode);
      // recorderNode는 destination에 연결할 필요가 없으므로 생략 (오디오 데이터를 수집만 함)

      // ************* 대체 로직 종료 *************

      setIsRecording(true);
      console.log('AudioWorklet 기반 PCM 녹음 시작');
    } catch (error) {
      console.error('마이크 접근 또는 녹음 중 오류 발생:', error);
      setIsRecording(false);
      alert('마이크 접근이 거부되었거나 오류가 발생했습니다.');
    }
  };

  const stopRecording = () => {
    if (audioContextRef.current) {
      // AudioWorkletNode 연결 해제
      processorRef.current.port.postMessage('stop'); // 프로세서에게 중지 알림 (선택적)
      inputPointRef.current.disconnect();
      processorRef.current.disconnect(); // 노드 연결 해제

      // ... (이후 AudioContext 닫기, 스트림 해제, PCM Blob 생성 로직은 동일) ...

      audioContextRef.current.close().then(() => {
        audioContextRef.current = null;
      });

      if (currentStreamRef.current) {
        currentStreamRef.current.getTracks().forEach((track) => track.stop());
        currentStreamRef.current = null;
      }

      // 모든 청크 연결 (이 로직은 동일합니다.)
      const combinedFloat32 = new Float32Array(
        audioChunksRef.current.reduce((acc, chunk) => acc + chunk.length, 0)
      );
      let offset = 0;
      for (const chunk of audioChunksRef.current) {
        combinedFloat32.set(chunk, offset);
        offset += chunk.length;
      }

      const tempAudioBuffer = {getChannelData: () => combinedFloat32};
      const pcmBlob = encodeToPCM(tempAudioBuffer);
      setRecordedPcmBlob(pcmBlob);

      setIsRecording(false);
      console.log('AudioWorklet 기반 PCM 녹음 중지 및 Blob 생성');
    }
  };

  const handleMicClick = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const handlePlayAudio = () => {
    if (currentAudioUrl && audioRef.current) {
      audioRef.current.play();
    }
  };

  // ---------------------- 답변 제출 로직 (WebSocket 전송으로 변경) ----------------------

  const handleNext = async () => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      alert('서버와의 연결이 끊겼습니다. 페이지를 새로고침 해 주세요.');
      return;
    }

    setIsSubmitting(true);
    setIsInterviewActive(false); // 답변 제출 중에는 새 답변 입력 비활성화

    // 1. 녹음 중이라면 먼저 중지 (가드)
    if (isRecording) {
      stopRecording();
      console.log('녹음을 먼저 중지했습니다. 다음 버튼을 다시 눌러주세요.');
      setIsSubmitting(false);
      return;
    }

    // 2. 유효성 검사 - 녹음된 오디오만 전송 (백엔드는 STT 처리)
    if (!recordedPcmBlob) {
      alert('답변을 녹음해 주세요.');
      setIsSubmitting(false);
      setIsInterviewActive(true);
      return;
    }

    try {
      // 3. Blob을 ArrayBuffer로 변환하여 전송
      const audioBuffer = await recordedPcmBlob.arrayBuffer();

      // 4. 오디오 데이터를 바이너리로 전송
      wsRef.current.send(audioBuffer);
      console.log('오디오 데이터 전송:', audioBuffer.byteLength, 'bytes');

      // 5. 답변 완료 메시지 전송
      wsRef.current.send(JSON.stringify({ type: 'answer_done' }));
      console.log('답변 완료 메시지 전송');

      // 6. UI 초기화 (다음 질문을 위해)
      setAnswer('');
      setRecordedPcmBlob(null);
      setCurrentQuestionIndex(prev => prev + 1);

      // 서버에서 다음 질문이 올 때까지 대기
      // handleWebSocketMessage에서 question_start를 받으면 isSubmitting을 false로 변경
    } catch (error) {
      console.error('답변 전송 오류:', error);
      alert('답변 전송 중 오류가 발생했습니다.');
      setIsSubmitting(false);
      setIsInterviewActive(true);
    }
  };

  const handleFinish = async () => {
    // 면접 종료 확정
    wsRef.current.send(JSON.stringify({type: 'END_INTERVIEW'}));
    navigate('/candidate/done');
  };

  // 제출 버튼 활성화 조건
  const isSubmitDisabled =
    isSubmitting ||
    isRecording ||
    !isInterviewActive || // 오디오 재생 완료 전에는 답변 불가
    (!answer.trim() && !recordedPcmBlob);

  return (
    <div className='w-full min-h-screen my-10'>
      <div className='w-2/3 flex flex-col items-center justify-center mx-auto px-6 py-12'>
        <div className='w-full flex flex-col items-start gap-2'>
          <span className='font-medium text-sm text-grey'>
            질문 {currentQuestionIndex + 1}
          </span>
          <h2 className='text-2xl font-bold tracking-tight text-dark md:text-3xl'>
            {currentQuestionText}
          </h2>
          {/* 오디오 엘리먼트는 숨겨진 채로 참조만 연결 */}
          <audio ref={audioRef} src={currentAudioUrl}></audio>
          <Button variant='ghost' onClick={handlePlayAudio}>
            질문 다시 듣기
          </Button>
        </div>

        {/* 중간 섹션: 마이크 버튼 */}
        <div className='flex flex-col items-center justify-center py-10 my-10'>
          <button
            onClick={handleMicClick}
            className={`relative flex h-28 w-28 items-center justify-center rounded-full transition-all ${
              isRecording
                ? 'bg-radial-[50%_50%_at_50%_50%] from-[#68ed68] from-38% to-[#73f58b] animate-pulse'
                : 'bg-radial-[50%_50%_at_50%_50%] from-[#7D63FF] from-38% to-[#AB9AFF] hover:bg-[#8B5CF6]/90'
            }`}
            aria-label={isRecording ? '녹음 중지' : '녹음 시작'}
            disabled={isSubmitting} // 제출 중에는 녹음 비활성화
          >
            <img className='h-10 w-10 text-white' src={mic} alt='녹음' />
          </button>
          <p className='pt-10 text-sm font-medium text-primary'>
            {isRecording
              ? '답변을 녹음 중입니다...'
              : recordedPcmBlob
              ? '답변 완료'
              : '마이크를 눌러 답변을 시작하세요.'}
          </p>
        </div>

        {/* 하단 섹션: 답변 입력 및 다음 버튼 */}
        <div className='w-full flex flex-col gap-5 items-center justify-center'>
          <textarea
            placeholder='답변을 입력하세요...'
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            className='w-full min-h-40 mx-auto p-3 border border-gray-200 rounded-lg focus:outline-2 focus:outline-primary/50 focus:border-primary'
          />
          <Button
            onClick={handleNext}
            disabled={
              isSubmitting ||
              isRecording ||
              (!answer.trim() && !recordedPcmBlob)
            }
            className='ml-auto disabled:opacity-50 disabled:bg-black'>
            {isSubmitting
              ? '저장 중...'
              : isLastQuestion
              ? '면접 종료'
              : '다음 질문'}
          </Button>
        </div>

        {/* Finish confirmation modal */}
        <ConfirmModal
          isOpen={showConfirmModal}
          onClose={() => setShowConfirmModal(false)}
          onConfirm={handleFinish}
          title='면접을 종료하시겠습니까?'
          message='모든 답변이 저장되었습니다. 면접을 종료하고 결과 페이지로 이동합니다.'
          confirmText='종료하기'
          cancelText='취소'
          variant='primary'
        />
      </div>
    </div>
  );
};

export default AIInterview;

