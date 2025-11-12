// 1. AudioWorkletProcessor 클래스 정의
class RecorderProcessor extends AudioWorkletProcessor {
    constructor() {
      super();
      // 데이터 전송을 위한 메시지 포트
      this.port.onmessage = (event) => {
        // 필요에 따라 메인 스레드에서 메시지를 받을 수 있음 (예: 녹음 시작/중지)
        if (event.data === 'stop') {
          // 녹음 중지 로직 구현 가능
        }
      };
    }
  
    // 2. 오디오 처리 메서드: 입력(input)을 받아 출력(output)을 생성
    // 오디오 데이터는 inputs[0]에 Float32Array 형태로 들어옴
    process(inputs, outputs, parameters) {
      if (inputs.length > 0 && inputs[0].length > 0) {
        const channelData = inputs[0][0]; // 첫 번째 입력의 첫 번째 채널 (모노)
  
        // 3. 데이터를 메인 스레드로 전송
        // JSON.stringify 없이 ArrayBuffer를 직접 전송하면 효율적임
        this.port.postMessage(channelData.buffer, [channelData.buffer]);
      }
  
      // true를 반환하여 노드가 활성화 상태를 유지하도록 함
      return true;
    }
  }
  
  // 4. 프로세서 등록
  registerProcessor('recorder-processor', RecorderProcessor);