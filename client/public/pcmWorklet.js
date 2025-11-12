class PCMWriterProcessor extends AudioWorkletProcessor {
  process(inputs, outputs, parameters) {
    const input = inputs[0];
    if (!input || input.length === 0) return true;

    const channelData = input[0]; // 첫 번째 채널만 사용 (mono)
    const buffer = new ArrayBuffer(channelData.length * 2); // 16bit PCM
    const view = new DataView(buffer);

    for (let i = 0; i < channelData.length; i++) {
      // Float32(-1~1) → Int16(PCM)
      let s = Math.max(-1, Math.min(1, channelData[i]));
      view.setInt16(i * 2, s < 0 ? s * 0x8000 : s * 0x7fff, true);
    }

    // PCM 데이터 버퍼를 메인 스레드로 전송
    this.port.postMessage(buffer);

    return true; // 계속 처리
  }
}

// “pcm-writer”라는 이름으로 등록
registerProcessor('pcm-writer', PCMWriterProcessor);
