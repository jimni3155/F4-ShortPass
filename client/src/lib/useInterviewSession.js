import {useCallback, useEffect, useRef, useState} from 'react';

export const SESSION_STATE = {
  CONNECTING: 'connecting',
  READY: 'ready',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
  ABORTED: 'aborted',
  ERROR: 'error',
};

export const TURN_STATE = {
  IDLE: 'idle',
  QUESTIONING: 'questioning',
  ANSWERING: 'answering',
  PROCESSING: 'processing',
  END: 'end',
};

export default function useInterviewSession({websocketUrl}) {
  const socketRef = useRef(null);

  const [sessionState, setSessionState] = useState(SESSION_STATE.CONNECTING);
  const [turnState, setTurnState] = useState(TURN_STATE.IDLE);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [sttText, setSttText] = useState('');
  const [logs, setLogs] = useState([]);
  const [error, setError] = useState(null);

  const audioRef = useRef(null);

  // onclose 에서 최신 sessionState를 보기 위한 ref
  const sessionStateRef = useRef(sessionState);
  useEffect(() => {
    sessionStateRef.current = sessionState;
  }, [sessionState]);

  /** ---------------------------
   *  질문 오디오 재생 helper
   ----------------------------*/
  const playAudioFromUrl = useCallback((url, onEnded) => {
    try {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }

      const audio = new Audio(url);
      audioRef.current = audio;

      audio.onended = () => {
        onEnded && onEnded();
      };

      audio.play().catch((e) => {
        console.error('Audio play blocked / error:', e);
        onEnded && onEnded();
      });
    } catch (e) {
      console.error('audio setup error', e);
      onEnded && onEnded();
    }
  }, []);

  /** ---------------------------
   *  로그 append
   ----------------------------*/
  const appendLog = useCallback((msg) => {
    setLogs((prev) => [...prev, msg]);
  }, []);

  /** ---------------------------
   *  socket getter (useAudioStreaming 에서 사용)
   ----------------------------*/
  const getSocket = useCallback(() => {
    return socketRef.current;
  }, []);

  /** ---------------------------
   *  WebSocket 연결
   ----------------------------*/
  const connect = useCallback(() => {
    if (!websocketUrl) {
      setError('No WebSocket URL');
      setSessionState(SESSION_STATE.ERROR);
      return;
    }

    setSessionState(SESSION_STATE.CONNECTING);
    const socket = new WebSocket(websocketUrl);
    socketRef.current = socket;

    socket.onopen = () => {
      console.log('[WS] open');
      setSessionState(SESSION_STATE.READY);
      appendLog('WebSocket connected');

      socket.send(JSON.stringify({type: 'start_interview'}));
    };

    /** ---------------------------
     * WebSocket 메시지 처리
     ----------------------------*/
    socket.onmessage = (event) => {
      console.log('[WS raw message]', event.data);
      const raw = event.data;

      /** (A) 문자열 메시지(JSON) */
      if (typeof raw === 'string') {
        let data;
        try {
          data = JSON.parse(raw);
        } catch (e) {
          console.error('[WS] JSON parse err:', e, raw);
          return;
        }

        const {type} = data;

        /** 연결 성공 */
        if (type === 'connection_success') {
          appendLog(data.message);
          return;
        }

        /** 질문 + 오디오 URL */
        if (type === 'question_audio') {
          console.log('[WS] question_audio 받은 데이터:', data);
          setSessionState(SESSION_STATE.IN_PROGRESS);
          setTurnState(TURN_STATE.QUESTIONING);

          setCurrentQuestionIndex((prev) => prev + 1);
          setCurrentQuestion({text: data.text});

          appendLog(`질문 ${currentQuestionIndex + 1}: ${data.text}`);

          if (data.audioUrl) {
            console.log('[WS] 질문 오디오 재생 URL:', data.audioUrl);
            playAudioFromUrl(data.audioUrl, () => {
              console.log('오디오 재생 완료');
              setTurnState(TURN_STATE.ANSWERING);
            });
          } else {
            setTurnState(TURN_STATE.ANSWERING);
          }

          return;
        }

        /** 질문(텍스트만) */
        if (type === 'question') {
          setSessionState(SESSION_STATE.IN_PROGRESS);
          setTurnState(TURN_STATE.QUESTIONING);
          setCurrentQuestionIndex((prev) => prev + 1);
          setCurrentQuestion({text: data.text});

          appendLog(`질문 ${currentQuestionIndex + 1}: ${data.text}`);
          return;
        }

        /** 질문 끝 신호 */
        if (type === 'question_end') {
          console.log('Question ended');
          return;
        }

        /** 상태 변경 */
        if (type === 'state') {
          if (data.turnState) {
            setTurnState(data.turnState.toLowerCase());
          }
          return;
        }

        /** STT final */
        if (type === 'stt_final') {
          setSttText(data.text);
          appendLog(`[STT 최종] ${data.text}`);
          return;
        }

        /** 인터뷰 종료 */
        if (type === 'interview_end') {
          setTurnState(TURN_STATE.END);
          setSessionState(SESSION_STATE.COMPLETED);
          appendLog('인터뷰가 종료되었습니다.');
          socket.close();
          return;
        }
      } else if (raw instanceof Blob) {
        // 지금은 URL 방식만 사용
        console.warn('[WS] Blob 수신 — 현재 URL 기반으로만 처리 중');
        return;
      }
    };

    /** 에러 처리 */
    socket.onerror = (e) => {
      console.error('[WS] error', e);
      setError('WebSocket error');
      setSessionState(SESSION_STATE.ERROR);
    };

    /** 소켓 종료 */
    socket.onclose = () => {
      console.log('[WS] onclose', code, reason);
      appendLog('WebSocket closed');
      const state = sessionStateRef.current;
      if (
        state !== SESSION_STATE.COMPLETED &&
        state !== SESSION_STATE.ABORTED
      ) {
        setSessionState(SESSION_STATE.ERROR);
      }
    };
  }, [appendLog, websocketUrl, playAudioFromUrl, currentQuestionIndex]);

  /** ---------------------------
   * next question
   ----------------------------*/
  const requestNextQuestion = useCallback(() => {
    const socket = socketRef.current;
    if (!socket || socket.readyState !== WebSocket.OPEN) return;
    socket.send(JSON.stringify({type: 'next_question'}));
  }, []);

  /** ---------------------------
   * 사용자가 수동으로 답변 종료
   ----------------------------*/
  const finishAnswerManually = useCallback(() => {
    const socket = socketRef.current;
    if (!socket || socket.readyState !== WebSocket.OPEN) return;

    socket.send(JSON.stringify({type: 'answer_end'}));
    setTurnState(TURN_STATE.PROCESSING);
  }, []);

  /** ---------------------------
   * 인터뷰 강제 종료
   ----------------------------*/
  const abortInterview = useCallback(() => {
    setSessionState(SESSION_STATE.ABORTED);
    setTurnState(TURN_STATE.END);

    const socket = socketRef.current;
    if (
      socket &&
      (socket.readyState === WebSocket.OPEN ||
        socket.readyState === WebSocket.CONNECTING)
    ) {
      socket.close(1000, 'client abort');
    }
  }, []);

  /** ---------------------------
   * mount 시 소켓 연결
   ----------------------------*/
  useEffect(() => {
    connect();

    return () => {
      const socket = socketRef.current;
      if (
        socket &&
        (socket.readyState === WebSocket.OPEN ||
          socket.readyState === WebSocket.CONNECTING)
      ) {
        socket.close(1000, 'unmount');
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [websocketUrl]);

  return {
    getSocket,
    sessionState,
    turnState,
    currentQuestion,
    currentQuestionIndex,
    sttText,
    logs,
    error,
    requestNextQuestion,
    finishAnswerManually,
    abortInterview,
  };
}
