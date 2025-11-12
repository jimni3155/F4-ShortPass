import {useRef} from 'react';

const STT_SERVER_URL = 'wss://your-backend/stt';

export function useSTT() {
  const socketRef = useRef(null);
  const transcriptCallbacks = useRef([]);
  const finalCallbacks = useRef([]);

  const startSTT = async () => {
    const newSocket = new WebSocket(STT_SERVER_URL);
    socketRef.current = newSocket;

    try {
      const stream = await navigator.mediaDevices.getUserMedia({audio: true});
      const audioCtx = new AudioContext();
      const source = audioCtx.createMediaStreamSource(stream);

      await audioCtx.audioWorklet.addModule('/pcmWorklet.js');
      const pcmWriterNode = new AudioWorkletNode(ctx, 'pcm-writer');
      source.connect(pcmWriterNode);

      pcmWriterNode.port.onmessage = (e) => newSocket.send(e.data);
      console.log('AudioWorklet node created successfully.');
    } catch (error) {
      console.error('Microphone access or AudioWorklet setup error:', error);
      alert('마이크 접근에 실패했습니다. 권한을 확인해주세요.');
    }

    // STT 서버 응답 처리
    newSocket.onmessage = (msg) => {
      try {
        const data = JSON.parse(msg.data);
        if (data.type === 'interim') {
          transcriptCallbacks.current.forEach((listener) => listener(text));
        } else if (data.type === 'final') {
          finalCallbacks.current.forEach((listener) => listener(text));
        }
      } catch (error) {
        console.error('Error parsing STT message:', error);
      }
    };

    // 연결 성공 시 초기 설정 메시지 전송
    newSocket.onopen = () => {
      newSocket.send(
        JSON.stringify({type: 'start', format: 'PCM16LE', sampleRate: 16000})
      );
    };
  };

  const stopSTT = () => {
    socketRef.current?.send(JSON.stringify({type: 'stop'}));
    socketRef.current?.close();
  };

  const onTranscript = (listener) => transcriptCallbacks.current.push(listener);
  const onFinal = (listener) => finalCallbacks.current.push(listener);

  return {startSTT, stopSTT, onTranscript, onFinal};
}
