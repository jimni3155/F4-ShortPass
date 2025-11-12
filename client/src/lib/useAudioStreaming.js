import {useRef, useState, useCallback, useEffect} from 'react';

// --- 기본 설정값 (필요시 조정 가능) ---
const RMS_THRESHOLD = 0.015; // 무음 판단 임계값 (0.01~0.03)
const SILENCE_DURATION_MS = 5000; // 5초 무음 → 자동 종료
const STT_SOCKET_URL = 'wss://'; // 실제 STT 서버 주소로 교체

export const STREAM_STATUS = {
  IDLE: 'idle',
  PREPARING: 'preparing',
  RECORDING: 'recording',
  STOPPING: 'stopping',
  CLOSED: 'closed',
  ERROR: 'error',
};

/**
 * 🎙 useAudioStreaming
 * 실시간 음성 스트리밍 (STT) 훅
 * - 답변 버튼 클릭 → WebSocket 연결 → 음성 스트리밍 전송
 * - 5초 이상 무음 → 자동 종료
 */
export default function useAudioStreaming() {
  const [status, setStatus] = useState(STREAM_STATUS.IDLE);
  const [isPaused, setIsPaused] = useState(false);
  const [rms, setRms] = useState(0);

  const socketRef = useRef(null);
  const mediaStreamRef = useRef(null);
  const audioContextRef = useRef(null);
  const workletRef = useRef(null);
  const vadIntervalRef = useRef(null);
  const lastVoiceTsRef = useRef(0);

  /** 🔹 녹음 일시정지 */
  const pauseRecording = useCallback(() => {
    if (status === STREAM_STATUS.RECORDING && !isPaused) {
      console.log('[Audio] Pausing recording');
      setIsPaused(true);
    }
  }, [status, isPaused]);

  /** 🔹 녹음 재개 */
  const resumeRecording = useCallback(() => {
    if (status === STREAM_STATUS.RECORDING && isPaused) {
      console.log('[Audio] Resuming recording');
      setIsPaused(false);
      lastVoiceTsRef.current = performance.now(); // 재개 시점부터 무음 다시 체크
    }
  }, [status, isPaused]);

  /** 🔹 리소스 정리 */
  const cleanup = useCallback(() => {
    clearInterval(vadIntervalRef.current);

    try {
      workletRef.current?.port && (workletRef.current.port.onmessage = null);
      workletRef.current?.disconnect();
      mediaStreamRef.current?.getTracks().forEach((t) => t.stop());
      audioContextRef.current?.close();
      socketRef.current?.close(1000, 'client-cleanup');
    } catch (err) {
      console.warn('[Cleanup] error:', err);
    }

    setRms(0);
  }, []);

  /** 🔹 스트리밍 종료 */
  const stopRecording = useCallback(() => {
    if (status !== STREAM_STATUS.RECORDING) return;
    setStatus(STREAM_STATUS.STOPPING);

    try {
      socketRef.current?.send(JSON.stringify({type: 'stop'}));
    } catch (err) {
      console.warn('[STT] stop send failed:', err);
    }

    cleanup();
    setStatus(STREAM_STATUS.CLOSED);
  }, [status, cleanup]);

  /** 🔹 무음 감지 타이머 */
  const startVadDetection = useCallback(() => {
    clearInterval(vadIntervalRef.current);
    vadIntervalRef.current = setInterval(() => {
      const silentFor = performance.now() - lastVoiceTsRef.current;
      if (silentFor >= SILENCE_DURATION_MS) {
        console.log(
          `[VAD] Silent for ${SILENCE_DURATION_MS / 1000}s → auto stop`
        );
        stopRecording();
      }
    }, 250);
  }, [stopRecording]);

  // 0️⃣ 서버에서 STT WebSocket URL을 받아오는 헬퍼
  // ✅ 0) 서버에서 STT WebSocket URL을 받아오는 헬퍼 (절대 URL 사용)
  async function fetchSttSocketUrl() {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 7000);

    try {
      // 반드시 프로토콜 포함!
      const API_BASE = 'http://52.91.161.156:8000';
      const endpoint = new URL(
        '/api/v1/interviews/prepare',
        API_BASE
      ).toString();

      const res = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify({
          candidateId: '1',
          companyId: '1',
          personaInstanceIds: ['1', '2'],
        }),
        signal: controller.signal,
      });

      if (!res.ok)
        throw new Error(`Failed to fetch STT URL (HTTP ${res.status})`);

      const data = await res.json();
      if (!data?.websocketUrl) throw new Error('Response missing "url" field');

      return data.websocketUrl; // e.g. "ws://52.91.161.156:8000/ws/stt/xyz"
    } finally {
      clearTimeout(timeout);
    }
  }

  /** 🔹 스트리밍 시작 */
  const startRecording = useCallback(async () => {
    if (
      status === STREAM_STATUS.RECORDING ||
      status === STREAM_STATUS.PREPARING
    )
      return;
    setStatus(STREAM_STATUS.PREPARING);

    try {
      // 1️⃣ 마이크 권한 요청
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
        video: false,
      });
      mediaStreamRef.current = stream;

      // 2️⃣ AudioContext + Worklet 설정
      const audioContext = new (window.AudioContext ||
        window.webkitAudioContext)({
        sampleRate: 16000,
      });
      await audioContext.audioWorklet.addModule('/pcmWorklet.js');
      const source = audioContext.createMediaStreamSource(stream);
      const worklet = new AudioWorkletNode(audioContext, 'pcm-writer');
      source.connect(worklet);

      audioContextRef.current = audioContext;
      workletRef.current = worklet;

      const Socket_Url = await fetchSttSocketUrl();
      if (!/^wss?:\/\//i.test(Socket_Url)) {
        throw new Error(`Invalid WS URL: ${Socket_Url}`);
      }

      // 3️⃣ WebSocket 연결
      const socket = new WebSocket(Socket_Url);
      socket.binaryType = 'arraybuffer';
      socketRef.current = socket;

      socket.onopen = () => {
        // STT 시작 신호
        socket.send(
          JSON.stringify({
            type: 'start',
            format: 'PCM16LE',
            sampleRate: 16000,
            lang: 'ko-KR',
          })
        );

        lastVoiceTsRef.current = performance.now();
        setStatus(STREAM_STATUS.RECORDING);
        startVadDetection();

        // 4️⃣ Worklet → WebSocket으로 전송
        worklet.port.onmessage = (e) => {
          const {type, rms: currentRms, payload} = e.data || {};
          if (type === 'level') {
            setRms(currentRms);
            if (currentRms > RMS_THRESHOLD) {
              lastVoiceTsRef.current = performance.now();
            }
          } else if (type === 'pcm') {
            if (
              socket.readyState === WebSocket.OPEN &&
              socket.bufferedAmount < 1_000_000
            ) {
              try {
                socket.send(payload);
              } catch {}
            }
          }
        };
      };

      socket.onerror = (err) => {
        console.error('[STT] Socket error:', err);
        setStatus(STREAM_STATUS.ERROR);
        cleanup();
      };

      socket.onclose = () => {
        cleanup();
        setStatus(STREAM_STATUS.CLOSED);
      };
    } catch (err) {
      console.error('[STT] startRecording failed:', err);
      setStatus(STREAM_STATUS.ERROR);
      cleanup();
    }
  }, [status, cleanup, startVadDetection]);

  /** 언마운트 시 자동 정리 */
  useEffect(() => cleanup, [cleanup]);

  return {
    status,
    rms,
    startRecording,
    stopRecording,
    STATUS: STREAM_STATUS,
  };
}
