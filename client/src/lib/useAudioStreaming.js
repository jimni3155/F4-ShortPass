// useAudioStreaming.js
import {useCallback, useEffect, useRef, useState} from 'react';

export const STREAM_STATUS = {
  IDLE: 'idle',
  PREPARING: 'preparing',
  RECORDING: 'recording',
  ERROR: 'error',
  CLOSED: 'closed',
};

// VAD용 임계값 (RMS)
const VAD_THRESHOLD = 0.01;
// 무음 허용 시간(ms)
const SILENCE_TIMEOUT = 4000;

export default function useAudioStreaming({getSocket, turnState} = {}) {
  const [status, setStatus] = useState(STREAM_STATUS.IDLE);
  const [rms, setRms] = useState(0);

  const audioContextRef = useRef(null);
  const mediaStreamRef = useRef(null);
  const workletRef = useRef(null);

  const lastVoiceTsRef = useRef(0);
  const hasSentAutoEndRef = useRef(false); // 자동 answer_end 중복 방지

  /** ===========================
   *  녹음 시작
   *  =========================== */
  const startRecording = useCallback(async () => {
    if (!getSocket) {
      console.warn('startRecording() called without getSocket');
      return;
    }

    const socket = getSocket();
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      console.warn('socket not ready, skip recording');
      return;
    }

    if (
      status === STREAM_STATUS.PREPARING ||
      status === STREAM_STATUS.RECORDING
    ) {
      // 이미 녹음 중이거나 준비 중이면 무시
      return;
    }

    setStatus(STREAM_STATUS.PREPARING);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
        },
        video: false,
      });

      mediaStreamRef.current = stream;

      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      const ctx = new AudioCtx({
        sampleRate: 16000,
      });

      await ctx.audioWorklet.addModule('/pcmWorklet.js');

      const source = ctx.createMediaStreamSource(stream);
      const worklet = new AudioWorkletNode(ctx, 'pcm-writer');

      source.connect(worklet);

      audioContextRef.current = ctx;
      workletRef.current = worklet;

      // VAD 초기화
      const now = performance.now();
      lastVoiceTsRef.current = now;
      hasSentAutoEndRef.current = false;

      worklet.port.onmessage = (e) => {
        const data = e.data;
        if (!data || typeof data !== 'object') return;

        const {type, payload, rms: newRms} = data;

        // 🔹 레벨/VAD용 메시지
        if (type === 'level') {
          if (typeof newRms === 'number') {
            setRms(newRms);
            if (newRms > VAD_THRESHOLD) {
              // 소리가 나면 마지막 발성 시점 갱신
              lastVoiceTsRef.current = performance.now();
              hasSentAutoEndRef.current = false; // 다시 말하면 autoEnd 가능 상태로
            }
          }
          return;
        }

        // 🔹 PCM 전송
        if (type === 'pcm' && payload) {
          if (socket.readyState === WebSocket.OPEN) {
            try {
              socket.send(payload);
            } catch (err) {
              console.error('socket send failed:', err);
            }
          }
          return;
        }
      };

      setStatus(STREAM_STATUS.RECORDING);
    } catch (err) {
      console.error('startRecording failed:', err);
      setStatus(STREAM_STATUS.ERROR);
    }
  }, [getSocket, status]);

  /** ===========================
   *  녹음 종료
   *  =========================== */
  const stopRecording = useCallback(() => {
    try {
      if (audioContextRef.current) {
        audioContextRef.current.close().catch(() => {});
      }
    } catch (_) {}

    audioContextRef.current = null;

    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((t) => t.stop());
    }
    mediaStreamRef.current = null;
    workletRef.current = null;

    setStatus(STREAM_STATUS.IDLE);
    setRms(0);
    hasSentAutoEndRef.current = false;
  }, []);

  /** ===========================
   *  무음(VAD) 감지 Polling
   *  =========================== */
  useEffect(() => {
    if (status !== STREAM_STATUS.RECORDING) return;
    if (!getSocket) return;

    const id = setInterval(() => {
      const socket = getSocket();
      if (!socket || socket.readyState !== WebSocket.OPEN) return;

      // 답변 중(ANSWERING)일 때만 VAD 적용
      if (turnState !== 'answering') return;

      const now = performance.now();
      const diff = now - lastVoiceTsRef.current;

      // 일정 시간 이상 무음 + 아직 autoEnd 안 보냈으면
      if (diff > SILENCE_TIMEOUT && !hasSentAutoEndRef.current) {
        console.log(
          '[VAD] silence detected, sending answer_end (diff:',
          diff,
          ')'
        );
        try {
          socket.send(JSON.stringify({type: 'answer_end'}));
          hasSentAutoEndRef.current = true;
        } catch (err) {
          console.error('failed to send answer_end:', err);
        }
      }
    }, 300);

    return () => clearInterval(id);
  }, [status, getSocket, turnState]);

  return {
    status,
    rms,
    startRecording,
    stopRecording,
    STATUS: STREAM_STATUS,
  };
}
