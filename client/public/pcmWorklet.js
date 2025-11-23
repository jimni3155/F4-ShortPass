// pcmWorklet.js

class PCMWriterProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
  }

  process(inputs) {
    const input = inputs[0];
    if (!input || input.length === 0) return true;

    const channelData = input[0]; // mono
    if (!channelData) return true;

    const frameLength = channelData.length;

    // Float32(-1~1) -> Int16(PCM)
    const buffer = new ArrayBuffer(frameLength * 2); // 16bit PCM
    const view = new DataView(buffer);

    let sumSquares = 0;

    for (let i = 0; i < frameLength; i++) {
      let s = channelData[i];
      // clamp
      s = Math.max(-1, Math.min(1, s));

      sumSquares += s * s;

      // Int16 리틀엔디언
      const int16 = s < 0 ? s * 0x8000 : s * 0x7fff;
      view.setInt16(i * 2, int16, true);
    }

    // RMS 계산
    const rms = Math.sqrt(sumSquares / frameLength) || 0;

    // 레벨 정보 (VAD용)
    this.port.postMessage({
      type: 'level',
      rms,
    });

    // PCM 데이터 (서버 전송용)
    // 성능을 위해 buffer를 transferable로 넘겨줌
    this.port.postMessage(
      {
        type: 'pcm',
        payload: buffer,
      },
      [buffer]
    );

    return true; // 계속 처리
  }
}

registerProcessor('pcm-writer', PCMWriterProcessor);
