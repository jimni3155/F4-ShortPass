# /api/endpoints/interview.py

# (수정) Request 객체를 임포트합니다.
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Path, Request 
from starlette.websockets import WebSocketState
from sqlalchemy.orm import Session
from db.database import get_db
from services import interview_service_v2 as interview_service
from models.interview import InterviewSession, InterviewStatus
from schemas.interview import PrepareInterviewRequest, PrepareInterviewResponse # (수정된 스키마 임포트)
from datetime import datetime
import os
import json

router = APIRouter()


@router.post("/interviews/prepare", response_model=PrepareInterviewResponse)
async def prepare_interview(
    request_data: PrepareInterviewRequest,
    fastapi_request: Request,
    db: Session = Depends(get_db)
):
    """
    면접 세션을 준비하고,
    클라이언트가 접속할 WebSocket URL을 반환합니다.

    1:1 구조: 1개 회사 + 여러 페르소나 순차 패널
    """
    try:
        # 지원자 ID와 회사 ID를 정수로 변환
        applicant_id = int(request_data.candidateId)
        company_id = int(request_data.companyId)
        persona_instance_ids = [int(pid) for pid in request_data.personaInstanceIds]

        # InterviewSession 생성 (1:1 구조)
        new_session = InterviewSession(
            applicant_id=applicant_id,
            company_id=company_id,
            status=InterviewStatus.PENDING,
            current_question_index=0,
            current_persona_index=0,
            created_at=datetime.utcnow()
        )

        db.add(new_session)
        db.commit()
        db.refresh(new_session)

        # SessionPersona 생성 (순차 패널)
        from models.interview import SessionPersona
        for idx, persona_instance_id in enumerate(persona_instance_ids):
            session_persona = SessionPersona(
                session_id=new_session.id,
                persona_instance_id=persona_instance_id,
                order=idx,
                role="primary"
            )
            db.add(session_persona)

        db.commit()

        # WebSocket URL 생성
        ws_protocol = "wss" if fastapi_request.url.scheme == "https" else "ws"
        host_and_port = fastapi_request.url.netloc

        # ws_url = f"{ws_protocol}://{host_and_port}/ws/interview/{new_session.id}"
        ws_url = f"{ws_protocol}://{host_and_port}/api/v1/ws/interview/{new_session.id}"
        print(f"생성된 WebSocket URL: {ws_url}")

        # API 응답 반환
        return PrepareInterviewResponse(
            interviewId=new_session.id,
            applicantId=new_session.applicant_id,
            companyId=new_session.company_id,
            personaInstanceIds=persona_instance_ids,
            status="pending",
            message="면접이 준비되었습니다.",
            websocketUrl=ws_url
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"잘못된 ID 형식입니다: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"면접 준비 실패: {str(e)}")


@router.websocket("/ws/interview/{interview_id}")
async def websocket_endpoint(websocket: WebSocket, interview_id: int = Path(...)):
    """
    WebSocket 연결을 수락하고,
    모든 처리를 서비스 계층(interview_service)으로 넘깁니다.

    Path Parameters: (주석 수정)
        interview_id: 준비된 면접 세션 ID
    """
    
    await websocket.accept()
    # 테스트를 위해 임시 주석처리
    """
    print(f"API: 클라이언트 연결됨 (interview_id={interview_id})") # 프론트 연결 테스트용 - 삭제예정

    try:
        # (중요) 실제 로직은 서비스 계층이 모두 처리
        await interview_service.handle_interview_session(websocket, interview_id)
    """

    # 테스트용 임시 코드
    try:
        await websocket.send_json({
            "type": "connection_success",
            "message": f"WebSocket 연결 성공! (Interview ID: {interview_id})"
        })

        # 2. (추가) 'start_interview' 신호를 기다리는 루프
        start_signal_received = False
        while not start_signal_received:
            message = await websocket.receive()
            if "text" in message:
                try:
                    data = json.loads(message["text"])
                    if data.get("type") == "start_interview":
                        print("API: 'start_interview' 신호 수신. 테스트 질문 전송 시작.")
                        start_signal_received = True # 루프 탈출
                        await websocket.send_json({
                            "type": "ack_start", # (응답) 시작 신호 잘 받았음
                            "message": "서버가 'start_interview' 신호를 받았습니다. 면접을 시작합니다."
                        })
                    else:
                         print(f"API: 'start_interview' 대기 중... 알 수 없는 텍스트 수신: {message['text']}")
                except json.JSONDecodeError:
                    print(f"API: 'start_interview' 대기 중... 비-JSON 텍스트 수신: {message['text']}")
            elif "bytes" in message:
                print("API: 'start_interview' 대기 중... 오디오 바이트가 먼저 수신됨 (무시).")

        # 3. 테스트 질문(TTS) 전송
        await websocket.send_json({ # (수정) await 누락 수정
            "type": "question",
            "text": "안녕하세요. 자기소개를 해 주세요."
        })
        TEST_MP3_PATH = "./test_polly_output.mp3"

        connection_lost = False # (수정) 연결 끊김 플래그 변수

        if os.path.exists(TEST_MP3_PATH):
            # 파일을 바이너리(rb) 모드로 엽니다
            with open(TEST_MP3_PATH, 'rb') as f:
                chunk_size = 1024 # 1KB씩 쪼개서 보냄
                # while True:
                    # chunk = f.read(chunk_size)
                    # if not chunk:
                    #     break # 파일 끝
                data = f.read()


                if websocket.state == WebSocketState.CONNECTED:
                    await websocket.send_bytes(chunk)
                else:
                    print("API: MP3 전송 중 클라이언트 연결 끊김.")
                    connection_lost = True # (수정) 플래그 설정
                    # break
            
            # (수정) 로그 메시지를 명확하게 분기
            if not connection_lost:
                print("API: MP3 파일 전송 완료.")
            else:
                print("API: MP3 전송 루프 중단됨 (연결 끊김).")
        else:
            print(f"!!! 경고: 테스트 MP3 파일({TEST_MP3_PATH})을 찾을 수 없습니다. MP3 전송을 건너뜁니다.")
            # (파일이 없으면 그냥 텍스트만 보낸 셈이 됨)

        # (수정) 연결이 끊겼다면, question_end를 보내지 말고 예외 발생
        if connection_lost:
            print("API: 클라이언트 연결이 끊겨 question_end 전송 스킵.")
            # except WebSocketDisconnect 블록으로 바로 이동시킴
            raise WebSocketDisconnect("MP3 전송 중 클라이언트 연결 끊김") 

        # 4. 질문 음성(TTS)이 끝났다는 신호 전송
        await websocket.send_json({"type": "question_end"})
        print("API: 테스트 질문 전송 완료. 답변 대기 중...")
        
        while True:
            # (주의) React가 오디오(bytes)를 보낼 경우:
            message = await websocket.receive()
            
            if "bytes" in message:
                received_bytes = message["bytes"]
                print(f"API: 클라이언트로부터 {len(received_bytes)} bytes 수신")
                await websocket.send_json({
                    "type": "echo_bytes",
                    "message": f"서버가 {len(received_bytes)} bytes 수신함."
                })
                
            if "text" in message:
                received_text = message["text"]
                print(f"API: 클라이언트로부터 텍스트 수신: {received_text}")
                await websocket.send_json({
                    "type": "echo_text",
                    "message": f"서버가 '{received_text}' 텍스트 수신함."
                })


    except WebSocketDisconnect:
        print(f"API: 클라이언트 연결 종료됨. (ID: {interview_id})")
    except Exception as e:
        print(f"API: 예외 발생 (ID: {interview_id}) - {e}")
        if websocket.state == WebSocketState.CONNECTED:
             await websocket.close(code=1011) # 서버 에러