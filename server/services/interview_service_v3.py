# 20251121 채아
# server/services/interview_service_v3.py

# 테스트 로직을 api/interview 에서 분리함

from fastapi import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState
import json
import os
from pathlib import Path
from utils.s3_uploader import upload_file_and_get_url

class InterviewServiceV3:
    async def handle_test_interview(self, websocket: WebSocket, interview_id: int):
        """
        웹소켓 연결부터 테스트 면접 진행(S3 업로드 -> 질문 전송 -> 에코)까지의
        전체 로직을 담당합니다.
        """
        
        # 1. 연결 성공 메시지 전송
        await websocket.send_json({
            "type": "connection_success",
            "message": f"WebSocket 연결 성공! (Interview ID: {interview_id})"
        })

        # 2. 'start_interview' 신호 대기
        await self._wait_for_start_signal(websocket)

        # 3. 테스트 질문(TTS) S3 업로드 및 전송
        await self._process_question_audio(websocket, interview_id)

        # 4. 답변(Echo) 루프 진입
        await self._start_echo_loop(websocket)

    async def _wait_for_start_signal(self, websocket: WebSocket):
        """클라이언트로부터 start_interview 신호를 기다립니다."""
        start_signal_received = False
        while not start_signal_received:
            message = await websocket.receive()
            if "text" in message:
                try:
                    data = json.loads(message["text"])
                    if data.get("type") == "start_interview":
                        print("SERVICE: 'start_interview' 신호 수신. 로직 시작.")
                        start_signal_received = True
                        await websocket.send_json({
                            "type": "ack_start",
                            "message": "면접을 시작합니다."
                        })
                    else:
                        print(f"SERVICE: 대기 중... 알 수 없는 텍스트: {message['text']}")
                except json.JSONDecodeError:
                    print("SERVICE: JSON 파싱 에러")
            elif "bytes" in message:
                print("SERVICE: 대기 중... 바이트 수신 무시.")

    async def _process_question_audio(self, websocket: WebSocket, interview_id: int):
        """MP3 파일을 찾아서 S3에 올리고 URL을 전송합니다."""
        
        # [중요] 서비스 파일 위치(services/) 기준으로 api/endpoints/ 내부의 mp3 경로 계산
        # 구조: root/services/this_file.py  <->  root/api/endpoints/mp3_file
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent 
        test_mp3_path = project_root / "api" / "test_polly_output.mp3"
        
        # 문자열로 변환
        test_mp3_path_str = str(test_mp3_path)
        question_text = "안녕하세요. 자기소개를 해 주세요."

        print(f"SERVICE: MP3 경로 확인 -> {test_mp3_path_str}")

        if os.path.exists(test_mp3_path_str):
            print("SERVICE: S3 업로드 시작...")
            audio_url = upload_file_and_get_url(test_mp3_path_str, folder=f"interview_{interview_id}")

            if audio_url:
                print(f"SERVICE: S3 업로드 완료. URL 전송.")
                await websocket.send_json({
                    "type": "question_audio",
                    "text": question_text,
                    "audioUrl": audio_url
                })
            else:
                print("SERVICE: S3 업로드 실패. 텍스트만 전송.")
                await websocket.send_json({
                    "type": "question",
                    "text": question_text
                })
        else:
            print(f"SERVICE: 파일 없음({test_mp3_path_str}). 텍스트만 전송.")
            await websocket.send_json({
                "type": "question",
                "text": question_text
            })

        # 질문 전송 완료 신호
        await websocket.send_json({"type": "question_end"})
        print("SERVICE: 질문 전송 완료. 답변 대기 중...")

    async def _start_echo_loop(self, websocket: WebSocket):
        """클라이언트 답변을 받아 그대로 돌려주는 에코 루프"""
        while True:
            message = await websocket.receive()
            
            if "bytes" in message:
                received_bytes = message["bytes"]
                print(f"SERVICE: {len(received_bytes)} bytes 수신")
                await websocket.send_json({
                    "type": "echo_bytes",
                    "message": f"서버가 {len(received_bytes)} bytes 수신함."
                })
                
            if "text" in message:
                received_text = message["text"]
                print(f"SERVICE: 텍스트 수신: {received_text}")
                await websocket.send_json({
                    "type": "echo_text",
                    "message": f"서버가 '{received_text}' 텍스트 수신함."
                })

interview_service_v3 = InterviewServiceV3()