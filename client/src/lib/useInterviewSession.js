// import {useCallback, useEffect, useRef, useState} from 'react';

// export const SESSION_STATE = {
//   CONNECTING: 'connecting',
//   READY: 'ready',
//   IN_PROGRESS: 'in_progress',
//   COMPLETED: 'completed',
//   ABORTED: 'aborted',
//   ERROR: 'error',
// };

// export const TURN_STATE = {
//   IDLE: 'idle',
//   QUESTIONING: 'questioning',
//   ANSWERING: 'answering',
//   PROCESSING: 'processing',
//   END: 'end',
// };

// export default function useInterviewSession({websocketUrl}) {
//   const socketRef = useRef(null);

//   const [sessionState, setSessionState] = useState(SESSION_STATE.CONNECTING);
//   const [turnState, setTurnState] = useState(TURN_STATE.IDLE);
//   const [currentQuestion, setCurrentQuestion] = useState(null);
//   const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
//   const [questionList, setQuestionList] = useState([]);
//   const [personaInfo, setPersonaInfo] = useState(null);
//   const [interviewers, setInterviewers] = useState([]);
//   const [currentInterviewer, setCurrentInterviewer] = useState(null);
//   const [sttText, setSttText] = useState('');
//   const [interviewResults, setInterviewResults] = useState([]);
//   const [transcriptUrl, setTranscriptUrl] = useState(null);
//   const [logs, setLogs] = useState([]);
//   const [messages, setMessages] = useState([]);
//   const [error, setError] = useState(null);

//   const audioRef = useRef(null);

//   // onclose 에서 최신 sessionState를 보기 위한 ref
//   const sessionStateRef = useRef(sessionState);
//   useEffect(() => {
//     sessionStateRef.current = sessionState;
//   }, [sessionState]);

//   /** ---------------------------
//    *  질문 오디오 재생 helper
//    ----------------------------*/
//   const playAudioFromUrl = useCallback((url, onEnded) => {
//     try {
//       if (audioRef.current) {
//         audioRef.current.pause();
//         audioRef.current = null;
//       }

//       const audio = new Audio(url);
//       audioRef.current = audio;

//       audio.onended = () => {
//         onEnded && onEnded();
//       };

//       audio.play().catch((e) => {
//         console.error('Audio play blocked / error:', e);
//         onEnded && onEnded();
//       });
//     } catch (e) {
//       console.error('audio setup error', e);
//       onEnded && onEnded();
//     }
//   }, []);

//   /** ---------------------------
//    *  로그 append
//    ----------------------------*/
//   const appendLog = useCallback((msg) => {
//     setLogs((prev) => [...prev, msg]);
//   }, []);

//   /** ---------------------------
//    *  socket getter (useAudioStreaming 에서 사용)
//    ----------------------------*/
//   const getSocket = useCallback(() => {
//     return socketRef.current;
//   }, []);

//   /** ---------------------------
//    *  WebSocket 연결
//    ----------------------------*/
//   const connect = useCallback(() => {
//     if (!websocketUrl) {
//       setError('No WebSocket URL');
//       setSessionState(SESSION_STATE.ERROR);
//       return;
//     }

//     setSessionState(SESSION_STATE.CONNECTING);
//     const socket = new WebSocket(websocketUrl);
//     socketRef.current = socket;

//     socket.onopen = () => {
//       console.log('[WS] open');
//       setSessionState(SESSION_STATE.READY);
//       appendLog('WebSocket connected');

//       socket.send(JSON.stringify({type: 'start_interview'}));
//     };

//     /** ---------------------------
//      * WebSocket 메시지 처리
//      ----------------------------*/
//     socket.onmessage = (event) => {
//       console.log('[WS raw message]', event.data);
//       const raw = event.data;

//       /** (A) 문자열 메시지(JSON) */
//       if (typeof raw === 'string') {
//         let data;
//         try {
//           data = JSON.parse(raw);
//         } catch (e) {
//           console.error('[WS] JSON parse err:', e, raw);
//           return;
//         }

//         const {type} = data;

//         /** 페르소나/질문 세트 수신 */
//         if (type === 'persona_info') {
//           if (data.persona) setPersonaInfo(data.persona);
//           if (Array.isArray(data.questions)) setQuestionList(data.questions);
//           appendLog('페르소나/질문 세트 로드 완료');
//           return;
//         }

//         /** 면접 정보 수신 (면접관 목록) */
//         if (type === 'interview_info') {
//           if (Array.isArray(data.interviewers)) {
//             setInterviewers(data.interviewers);
//             appendLog(`면접관 ${data.total_interviewers}명, 총 질문 ${data.total_questions}개`);
//           }
//           return;
//         }

//         /** 면접관 전환 */
//         if (type === 'interviewer_change') {
//           if (data.interviewer) {
//             setCurrentInterviewer(data.interviewer);
//             appendLog(`${data.interviewer.name}님의 면접 시작`);
//           }
//           return;
//         }

//         /** 면접관 종료 */
//         if (type === 'interviewer_complete') {
//           appendLog(data.message || '면접관 진행 완료');
//           return;
//         }

//         /** 연결 성공 */
//         if (type === 'connection_success') {
//           appendLog(data.message);
//           return;
//         }

//         /** 질문 + 오디오 URL */
//         if (type === 'question_audio') {
//           console.log('[WS] question_audio 받은 데이터:', data);
//           setSessionState(SESSION_STATE.IN_PROGRESS);
//           setTurnState(TURN_STATE.QUESTIONING);

//           setCurrentQuestionIndex((prev) => {
//             const next = prev + 1;
//             appendLog(`질문 ${next}: ${data.text}`);
//             return next;
//           });
//           setCurrentQuestion({text: data.text});

//           setMessages((prev) => [
//             ...prev,
//             {type: 'question', text: data.text, timestamp: Date.now()},
//           ]);

//           if (data.audioUrl) {
//             console.log('[WS] 질문 오디오 재생 URL:', data.audioUrl);
//             playAudioFromUrl(data.audioUrl, () => {
//               console.log('오디오 재생 완료');
//               setTurnState(TURN_STATE.ANSWERING);
//             });
//           } else {
//             setTurnState(TURN_STATE.ANSWERING);
//           }

//           return;
//         }

//         /** 꼬리질문 (follow-up question) */
//         if (type === 'follow_up_question') {
//           console.log('[WS] follow_up_question 받은 데이터:', data);
//           setTurnState(TURN_STATE.QUESTIONING);

//           appendLog(`[꼬리질문] ${data.text}`);
//           setCurrentQuestion({text: data.text, isFollowUp: true});

//           if (data.audioUrl) {
//             playAudioFromUrl(data.audioUrl, () => {
//               setTurnState(TURN_STATE.ANSWERING);
//             });
//           } else {
//             setTurnState(TURN_STATE.ANSWERING);
//           }

//           return;
//         }

//         /** 질문(텍스트만) */
//         // if (type === 'question') {
//         //   setSessionState(SESSION_STATE.IN_PROGRESS);
//         //   setTurnState(TURN_STATE.QUESTIONING);
//         //   setCurrentQuestionIndex((prev) => {
//         //     const next = prev + 1;
//         //     appendLog(`질문 ${next}: ${data.text}`);
//         //     return next;
//         //   });
//         //   setCurrentQuestion({text: data.text});
//         //   return;
//         // }

//         /** 질문 끝 신호 */
//         if (type === 'question_end') {
//           console.log('Question ended');
//           return;
//         }

//         /** 상태 변경 */
//         if (type === 'state') {
//           if (data.turnState) {
//             setTurnState(data.turnState.toLowerCase());
//           }
//           return;
//         }

//         /** STT final */
//         if (type === 'stt_final') {
//           setSttText(data.text);
//           appendLog(`[STT 최종] ${data.text}`);
//           setMessages((prev) => [
//             ...prev,
//             {type: 'answer', text: data.text, timestamp: Date.now()},
//           ]);

//           return;
//         }

//         /** 인터뷰 종료 */
//         if (type === 'interview_end') {
//           setTurnState(TURN_STATE.END);
//           setSessionState(SESSION_STATE.COMPLETED);
//           setInterviewResults(data.results || []);
//           setTranscriptUrl(data.transcriptUrl || null);
//           appendLog('인터뷰가 종료되었습니다.');
//           socket.close();
//           return;
//         }
//       } else if (raw instanceof Blob) {
//         // 지금은 URL 방식만 사용
//         console.warn('[WS] Blob 수신 — 현재 URL 기반으로만 처리 중');
//         return;
//       }
//     };

//     /** 에러 처리 */
//     socket.onerror = (e) => {
//       console.error('[WS] error', e);
//       setError('WebSocket error');
//       setSessionState(SESSION_STATE.ERROR);
//     };

//     /** 소켓 종료 */
//     socket.onclose = (event) => {
//       const {code, reason} = event || {};
//       console.log('[WS] onclose', code, reason);
//       appendLog('WebSocket closed');
//       const state = sessionStateRef.current;
//       if (
//         state !== SESSION_STATE.COMPLETED &&
//         state !== SESSION_STATE.ABORTED
//       ) {
//         setSessionState(SESSION_STATE.ERROR);
//       }
//     };
//   }, [appendLog, websocketUrl, playAudioFromUrl, currentQuestionIndex]);

//   /** ---------------------------
//    * next question
//    ----------------------------*/
//   const requestNextQuestion = useCallback(() => {
//     const socket = socketRef.current;
//     if (!socket || socket.readyState !== WebSocket.OPEN) return;
//     socket.send(JSON.stringify({type: 'next_question'}));
//   }, []);

//   /** ---------------------------
//    * 사용자가 수동으로 답변 종료
//    ----------------------------*/
//   const finishAnswerManually = useCallback(() => {
//     const socket = socketRef.current;
//     if (!socket || socket.readyState !== WebSocket.OPEN) return;

//     socket.send(JSON.stringify({type: 'answer_end'}));
//     setTurnState(TURN_STATE.PROCESSING);
//   }, []);

//   /** ---------------------------
//    * 인터뷰 강제 종료
//    ----------------------------*/
//   const abortInterview = useCallback(() => {
//     setSessionState(SESSION_STATE.ABORTED);
//     setTurnState(TURN_STATE.END);

//     const socket = socketRef.current;
//     if (
//       socket &&
//       (socket.readyState === WebSocket.OPEN ||
//         socket.readyState === WebSocket.CONNECTING)
//     ) {
//       socket.close(1000, 'client abort');
//     }
//   }, []);

//   /** ---------------------------
//    * mount 시 소켓 연결
//    ----------------------------*/
//   useEffect(() => {
//     connect();

//     return () => {
//       const socket = socketRef.current;
//       if (
//         socket &&
//         (socket.readyState === WebSocket.OPEN ||
//           socket.readyState === WebSocket.CONNECTING)
//       ) {
//         socket.close(1000, 'unmount');
//       }
//     };
//     // eslint-disable-next-line react-hooks/exhaustive-deps
//   }, [websocketUrl]);

//   return {
//     getSocket,
//     sessionState,
//     turnState,
//     currentQuestion,
//     currentQuestionIndex,
//     questionList,
//     personaInfo,
//     interviewers,
//     currentInterviewer,
//     sttText,
//     interviewResults,
//     transcriptUrl,
//     logs,
//     messages,
//     error,
//     requestNextQuestion,
//     finishAnswerManually,
//     abortInterview,
//   };
// }
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
  PROCESSING: 'processing', // 답변 처리 중 (로딩) 상태 활용
  END: 'end',
};

export default function useInterviewSession({websocketUrl}) {
  const socketRef = useRef(null);

  const [sessionState, setSessionState] = useState(SESSION_STATE.CONNECTING);
  const [turnState, setTurnState] = useState(TURN_STATE.IDLE);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [questionList, setQuestionList] = useState([]);
  const [personaInfo, setPersonaInfo] = useState(null);
  const [interviewers, setInterviewers] = useState([]);
  const [currentInterviewer, setCurrentInterviewer] = useState(null);
  const [sttText, setSttText] = useState('');
  const [interviewResults, setInterviewResults] = useState([]);
  const [transcriptUrl, setTranscriptUrl] = useState(null);
  const [logs, setLogs] = useState([]);
  const [messages, setMessages] = useState([]);
  const [error, setError] = useState(null);

  const audioRef = useRef(null);

  // onclose 에서 최신 sessionState를 보기 위한 ref
  const sessionStateRef = useRef(sessionState);
  useEffect(() => {
    sessionStateRef.current = sessionState;
  }, [sessionState]);

  /** ---------------------------
   * 질문 오디오 재생 helper
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
   * 로그 append
   ----------------------------*/
  const appendLog = useCallback((msg) => {
    setLogs((prev) => [...prev, msg]);
  }, []);

  /** ---------------------------
   * socket getter (useAudioStreaming 에서 사용)
   ----------------------------*/
  const getSocket = useCallback(() => {
    return socketRef.current;
  }, []);

  /** ---------------------------
   * WebSocket 연결
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
      // console.log('[WS raw message]', event.data); // 로그 너무 많으면 주석 처리
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

        /** 페르소나/질문 세트 수신 */
        if (type === 'persona_info') {
          if (data.persona) setPersonaInfo(data.persona);
          if (Array.isArray(data.questions)) setQuestionList(data.questions);
          appendLog('페르소나/질문 세트 로드 완료');
          return;
        }

        /** 면접 정보 수신 (면접관 목록) */
        if (type === 'interview_info') {
          if (Array.isArray(data.interviewers)) {
            setInterviewers(data.interviewers);
            appendLog(`면접관 ${data.total_interviewers}명, 총 질문 ${data.total_questions}개`);
          }
          return;
        }

        /** 면접관 전환 */
        if (type === 'interviewer_change') {
          if (data.interviewer) {
            setCurrentInterviewer(data.interviewer);
            appendLog(`${data.interviewer.name}님의 면접 시작`);
          }
          return;
        }

        /** 면접관 종료 */
        if (type === 'interviewer_complete') {
          appendLog(data.message || '면접관 진행 완료');
          return;
        }

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

          setCurrentQuestionIndex((prev) => {
            const next = prev + 1;
            appendLog(`질문 ${next}: ${data.text}`);
            return next;
          });
          setCurrentQuestion({text: data.text});

          // [수정] 질문을 받으면 메시지에 추가 (과거->최신 순서 유지)
          setMessages((prev) => [
            ...prev,
            {type: 'question', text: data.text, timestamp: Date.now()},
          ]);

          if (data.audioUrl) {
            console.log('[WS] 질문 오디오 재생 URL:', data.audioUrl);
            playAudioFromUrl(data.audioUrl, () => {
              console.log('오디오 재생 완료 -> 답변 시작');
              setTurnState(TURN_STATE.ANSWERING);
            });
          } else {
            setTurnState(TURN_STATE.ANSWERING);
          }

          return;
        }

        /** 꼬리질문 (follow-up question) */
        if (type === 'follow_up_question') {
          console.log('[WS] follow_up_question 받은 데이터:', data);
          setTurnState(TURN_STATE.QUESTIONING);

          appendLog(`[꼬리질문] ${data.text}`);
          setCurrentQuestion({text: data.text, isFollowUp: true});
          
          // [추가] 꼬리질문도 메시지 로그에 추가해야 함
          setMessages((prev) => [
            ...prev,
            {type: 'question', text: data.text, timestamp: Date.now()},
          ]);

          if (data.audioUrl) {
            playAudioFromUrl(data.audioUrl, () => {
              setTurnState(TURN_STATE.ANSWERING);
            });
          } else {
            setTurnState(TURN_STATE.ANSWERING);
          }

          return;
        }

        /** 질문 끝 신호 */
        if (type === 'question_end') {
          // 오디오 재생이 끝나는 시점에 상태 변경하므로 여기서는 로깅만
          console.log('Question audio ended signal received');
          return;
        }

        /** 상태 변경 */
        if (type === 'state') {
          if (data.turnState) {
            setTurnState(data.turnState.toLowerCase());
          }
          return;
        }

        /** [중요 수정] STT final (답변 완료) */
        if (type === 'stt_final') {
          appendLog(`[STT 최종] ${data.text}`);
          
          // 1. 확정된 답변을 메시지 리스트에 추가
          setMessages((prev) => [
            ...prev,
            {type: 'answer', text: data.text, timestamp: Date.now()},
          ]);
          
          // 2. [수정] 실시간 텍스트(sttText)를 비워서 '답변 중' 버블이 사라지게 함 (중복 표시 방지)
          setSttText(''); 
          
          return;
        }
        
        /** [추가] 답변 완료 확인 (ack_answer_end) */
        if (type === 'ack_answer_end') {
           // 답변이 서버에 잘 저장되었으므로, 상태를 처리 중(Processing)이나 대기(IDLE)로 변경
           // 다음 질문이 오기 전까지 잠깐의 공백 상태
           setTurnState(TURN_STATE.PROCESSING);
           return;
        }

        /** 인터뷰 종료 */
        if (type === 'interview_end') {
          setTurnState(TURN_STATE.END);
          setSessionState(SESSION_STATE.COMPLETED);
          setInterviewResults(data.results || []);
          setTranscriptUrl(data.transcriptUrl || null);
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
    socket.onclose = (event) => {
      const {code, reason} = event || {};
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
    // 즉시 Processing으로 바꿔서 UI 상에서 녹음 중지 상태로 변경
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
    questionList,
    personaInfo,
    interviewers,
    currentInterviewer,
    sttText,
    interviewResults,
    transcriptUrl,
    logs,
    messages,
    error,
    requestNextQuestion,
    finishAnswerManually,
    abortInterview,
  };
}