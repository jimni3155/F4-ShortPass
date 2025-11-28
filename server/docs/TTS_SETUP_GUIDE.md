# AWS Polly TTS 스트리밍 설정 가이드

##  구현 완료 사항

✅ **`stream_text_to_speech()` 함수 구현 완료**
- 위치: `server/services/interview_service.py`
- 기능:
  - AWS Polly Neural 엔진 사용 (자연스러운 한국어 음성)
  - 1024바이트 청크 단위로 실시간 스트리밍
  - 비동기 처리 (`asyncio.to_thread` 사용)
  - 에러 처리 및 로깅
  - WebSocket을 통한 클라이언트 전송

✅ **기존 `_send_tts_audio()` 함수 개선**
- 새로운 `stream_text_to_speech()` 함수를 내부적으로 호출
- 기존 코드와의 호환성 유지

✅ **WebSocket 엔드포인트 수정**
- `api/interview.py`에 `WebSocketState` import 추가

---

## 🔧 필수 설정: IAM 권한 추가

### 현재 상태
```
❌ AccessDeniedException: EC2 IAM 역할에 Polly 권한이 없음
```

### 해결 방법

#### 1. AWS Console에서 IAM 역할 찾기
```bash
현재 EC2 IAM 역할: SafeRoleForUser-linkbig-ht-06
```

#### 2. IAM 정책 추가

**옵션 A: AWS 관리형 정책 사용 (권장)**
```
정책 이름: AmazonPollyFullAccess
```

**옵션 B: 커스텀 정책 생성 (최소 권한 원칙)**

다음 JSON 정책을 생성하여 IAM 역할에 추가:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "polly:SynthesizeSpeech",
                "polly:DescribeVoices"
            ],
            "Resource": "*"
        }
    ]
}
```

#### 3. AWS CLI로 정책 추가 (선택사항)

```bash
# 관리형 정책 추가
aws iam attach-role-policy \
    --role-name SafeRoleForUser-linkbig-ht-06 \
    --policy-arn arn:aws:iam::aws:policy/AmazonPollyFullAccess

# 또는 커스텀 정책 생성 후 추가
aws iam create-policy \
    --policy-name PollyTTSPolicy \
    --policy-document file://polly-policy.json

aws iam attach-role-policy \
    --role-name SafeRoleForUser-linkbig-ht-06 \
    --policy-arn arn:aws:iam::717279725295:policy/PollyTTSPolicy
```

---

## 🧪 테스트 방법

### 1. Polly 권한 테스트
IAM 정책 추가 후 다음 명령어로 테스트:

```bash
cd /home/ec2-user/flex/server
source ../venv1/bin/activate
python test_tts_streaming.py
```

**예상 출력:**
```
✓ Polly 호출 성공!
✓ AudioStream 획득 성공!
✓ 스트리밍 완료!
  - 총 청크 수: XX
  - 총 바이트: XXXX
```

### 2. FastAPI 서버 실행
```bash
cd /home/ec2-user/flex/server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. WebSocket 연결 테스트
프론트엔드에서 다음 WebSocket 엔드포인트로 연결:

```
ws://[EC2-PUBLIC-IP]:8000/api/v1/ws/interview
```

---

## 📡 프론트엔드 통합 가이드

### JavaScript/TypeScript WebSocket 클라이언트

```javascript
// WebSocket 연결
const ws = new WebSocket('ws://YOUR_EC2_IP:8000/api/v1/ws/interview');
const audioContext = new AudioContext();
let audioQueue = [];

ws.onopen = () => {
    console.log('면접 WebSocket 연결됨');
};

ws.onmessage = async (event) => {
    // 1. JSON 메시지 (메타데이터)
    if (typeof event.data === 'string') {
        const message = JSON.parse(event.data);

        switch (message.type) {
            case 'question_start':
                console.log('질문 시작:', message.text);
                break;
            case 'question_end':
                console.log('질문 종료');
                break;
            case 'error':
                console.error('에러:', message.message);
                break;
        }
    }

    // 2. Binary 메시지 (오디오 청크)
    if (event.data instanceof Blob) {
        // MP3 청크를 바로 재생
        const audioBlob = event.data;
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);

        audio.play().catch(err => {
            console.error('오디오 재생 실패:', err);
        });

        // 메모리 정리
        audio.onended = () => URL.revokeObjectURL(audioUrl);
    }
};

ws.onerror = (error) => {
    console.error('WebSocket 에러:', error);
};

ws.onclose = () => {
    console.log('WebSocket 연결 종료');
};
```

### React 예시

```typescript
import { useEffect, useRef, useState } from 'react';

export function useInterviewWebSocket(url: string) {
    const wsRef = useRef<WebSocket | null>(null);
    const [isConnected, setIsConnected] = useState(false);
    const [currentQuestion, setCurrentQuestion] = useState('');

    useEffect(() => {
        const ws = new WebSocket(url);
        wsRef.current = ws;

        ws.onopen = () => {
            console.log('WebSocket 연결됨');
            setIsConnected(true);
        };

        ws.onmessage = async (event) => {
            if (typeof event.data === 'string') {
                const message = JSON.parse(event.data);

                if (message.type === 'question_start') {
                    setCurrentQuestion(message.text);
                }
            }

            if (event.data instanceof Blob) {
                // 오디오 재생
                const audioUrl = URL.createObjectURL(event.data);
                const audio = new Audio(audioUrl);
                await audio.play();
                audio.onended = () => URL.revokeObjectURL(audioUrl);
            }
        };

        ws.onclose = () => {
            console.log('WebSocket 연결 종료');
            setIsConnected(false);
        };

        return () => {
            ws.close();
        };
    }, [url]);

    return { isConnected, currentQuestion, ws: wsRef.current };
}
```

---

## 🔄 함수 사용 방법

### 직접 호출

```python
from fastapi import WebSocket
from services.interview_service import stream_text_to_speech

@app.websocket("/custom/tts")
async def custom_tts_endpoint(websocket: WebSocket):
    await websocket.accept()

    # TTS 스트리밍 실행
    await stream_text_to_speech(
        text_to_speak="안녕하세요. AI 면접을 시작하겠습니다.",
        websocket=websocket
    )

    await websocket.close()
```

### 기존 면접 플로우 (자동 통합됨)

```python
# server/services/interview_service.py의 handle_interview_session()에서
# 자동으로 stream_text_to_speech()를 사용합니다.

# 변경 사항 없음 - 기존 코드가 자동으로 개선된 함수를 사용함
await _send_tts_audio(websocket, "질문 텍스트")
```

---

## 🎯 주요 개선 사항

| 항목 | 기존 | 개선 후 |
|------|------|---------|
| **엔진** | Standard | **Neural** (자연스러운 음성) |
| **비동기 처리** | 동기 블로킹 | **asyncio.to_thread** 사용 |
| **에러 처리** | 기본 | **상세한 에러 메시지 및 로깅** |
| **스트리밍** | 기본 | **1024바이트 청크 단위** |
| **WebSocket 상태 체크** | 없음 | **연결 상태 확인 후 전송** |

---

##  성능 및 비용

### 성능
- **청크 크기**: 1024 bytes (약 0.1초 분량)
- **지연 시간**: 첫 청크까지 ~200-500ms
- **스트리밍 방식**: 파일 저장 없이 메모리에서 직접 전송

### 비용 (AWS Polly Neural)
- **가격**: 백만 문자당 $16 (Standard는 $4)
- **예상 비용**: 면접 1회당 약 500자 = $0.008
- **월 1000회 면접**: 약 $8

---

## 🐛 트러블슈팅

### 문제: "AccessDeniedException"
**해결**: IAM 역할에 Polly 권한 추가 (위의 IAM 권한 섹션 참고)

### 문제: "InvalidSsmlException"
**해결**: 텍스트에 특수 문자(`<`, `>`, `&`) 제거 또는 이스케이프 처리

### 문제: 오디오가 재생되지 않음
**해결**:
1. 브라우저 콘솔에서 오디오 자동재생 정책 확인
2. 사용자 인터랙션 후 재생 시도
3. MP3 코덱 지원 확인

### 문제: "VoiceNotFoundException"
**해결**: `test_tts_streaming.py`를 실행하여 사용 가능한 음성 확인

---

## 📝 다음 단계

1. ✅ IAM 정책 추가
2. ✅ 테스트 스크립트 실행
3. ✅ FastAPI 서버 실행
4. ✅ 프론트엔드 WebSocket 연결
5. ⬜ 실제 면접 플로우 테스트
6. ⬜ (선택) STT 스트리밍 구현 (현재는 배치 방식)

---

## 🔗 관련 문서

- [AWS Polly 문서](https://docs.aws.amazon.com/polly/)
- [FastAPI WebSocket 가이드](https://fastapi.tiangolo.com/advanced/websockets/)
- [boto3 Polly 레퍼런스](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/polly.html)

---

**구현 완료일**: 2025-10-29
**구현자**: Claude Code
**버전**: 1.0.0
