# server/services/interview_service.py
"""
면접 진행 서비스 (WebSocket 기반)
tts: OpenAI TTS (text-to-speech 변환)
stt: OpenAI Whisper (speech-to-text 변환)
"""

import boto3
import json
import time
import asyncio
import io
from fastapi import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState
from openai import OpenAI
from core.config import *
from services.interview_flow_manager import InterviewFlowManager
from ai.scorers.answer_scorer import AnswerScorer
from db.database import SessionLocal
from models.interview import InterviewSession, InterviewStatus, InterviewResult, Applicant, PersonaDB
from datetime import datetime
from sqlalchemy.orm import Session
from typing import Optional

# 필요한 클라이언트들 생성
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# --- 서비스 메인 함수 ---

async def handle_interview_session(websocket: WebSocket, interview_id: int):
    """
    WebSocket을 통한 면접 세션 핸들러. InterviewFlowManager 사용
    """
    print(f"Service: 면접 세션 핸들러 시작. (interview_id={interview_id})")

    # 데이터베이스 세션 생성
    db = SessionLocal()
    current_persona: Optional[PersonaDB] = None # 분기 단계에서 현재 질문하는 페르소나 추적

    try:
        # 1. 면접 세션 로드
        session, applicant, personas = await _initialize_interview(db, interview_id, websocket)
        if not session: return # 초기화 실패 시 종료

        applicant_name = applicant.name if applicant else "지원자"
        interview_manager = InterviewFlowManager(personas=personas, applicant_name=applicant_name)

# --- 면접 루프 ---
        while interview_manager.stage != InterviewStage.FINISHED:

            # --- 다음 질문 결정 ---
            if interview_manager.stage == InterviewStage.COMMON:
                current_question_text = interview_manager.get_next_common_question()
                current_persona = None # 공통 질문은 특정 페르소나가 아님
                if current_question_text is None:
                    # 공통 질문 종료 -> 분기 단계 시작
                    interview_manager.start_branched_stage()
                    # 분기 첫 질문을 위한 페르소나 선택 (여기서는 간단히 첫 번째 페르소나)
                    current_persona = personas[0]
                    # 분기 첫 질문은 답변 없이 바로 생성 요청 (또는 기본 질문 사용)
                    # 여기서는 일단 간단하게 첫 페르소나의 포커스 키워드로 질문 시작
                    current_question_text = f"{current_persona.focus_keywords[0]}에 대해 자세히 설명해주시겠어요?"
                    # 첫 분기 질문을 히스토리에 미리 추가
                    interview_manager.conversation_histories[current_persona.persona_id].append({
                         "role": "assistant", "content": current_question_text
                    })

            elif interview_manager.stage == InterviewStage.BRANCHED:
                # 이전 답변을 기반으로 현재 페르소나가 후속 질문 생성
                # (주의: _get_stt_answer 에서 받은 이전 답변(answer_text)을 사용해야 함)
                # 이 로직은 루프 시작 시점이 아니라 답변 처리 후에 와야 함 -> 로직 수정 필요
                pass # 아래 답변 처리 후 로직에서 처리

            if not current_question_text: # 더 이상 질문이 없으면 종료 (예외 처리)
                 interview_manager.finish_interview()
                 break

            # --- 질문 전달 (TTS) ---
            await _send_tts_audio(websocket, current_question_text)

            # --- 답변 수신 (STT) ---
            answer_text = await _get_stt_answer(websocket, str(interview_id), interview_manager.common_question_index + sum(interview_manager.branch_question_count.values()))

            if not answer_text: answer_text = "(답변이 없습니다.)"
            await websocket.send_json({"type": "answer_text", "text": answer_text})

            # --- 답변 저장 ---
            question_type = "common" if interview_manager.stage == InterviewStage.COMMON else "branched"
            persona_id_for_db = current_persona.persona_id if current_persona else None
            await _save_interview_result(db, interview_id, current_question_text, answer_text, question_type, persona_id_for_db)

            # --- 다음 단계 준비 (질문 생성 또는 종료) ---
            if interview_manager.stage == InterviewStage.COMMON:
                interview_manager.add_common_qa(current_question_text, answer_text)
                # 다음 공통 질문은 루프 시작 시 get_next_common_question() 에서 가져옴

            elif interview_manager.stage == InterviewStage.BRANCHED:
                if not current_persona: # 예외 케이스 방지
                    raise Exception("분기 단계에서 현재 페르소나가 설정되지 않았습니다.")

                await websocket.send_json({"type": "generating_question"})
                # 현재 페르소나의 답변 처리 및 다음 질문 생성
                next_question_text = interview_manager.process_branched_answer(current_persona, answer_text)

                # 면접 종료 조건 확인
                if interview_manager.should_finish_interview():
                    interview_manager.finish_interview()
                    break # 루프 종료

                # 다음 질문자 결정 (간단한 라운드 로빈 방식)
                current_persona_index = personas.index(current_persona)
                next_persona_index = (current_persona_index + 1) % len(personas)
                current_persona = personas[next_persona_index]

                # 생성된 질문을 다음 루프에서 사용할 질문으로 설정
                # (주의: process_branched_answer가 다음 질문을 생성했으므로, 다음 루프 시작 시 이를 사용해야 함)
                # -> 로직 수정: 다음 루프에서 사용할 current_question_text를 여기서 설정
                current_question_text = next_question_text # 다음 루프는 이 질문으로 시작

        # --- 면접 종료 처리 ---
        await _finalize_interview(db, interview_id, websocket, interview_manager)

    except WebSocketDisconnect:
        print(f"Service: 클라이언트({interview_id}) 연결 끊김.")
        await _update_session_status(db, interview_id, InterviewStatus.FAILED)
    except Exception as e:
        print(f"Service: 예외 발생 ({interview_id}): {e}")
        await _update_session_status(db, interview_id, InterviewStatus.FAILED)
        await _safe_send_error(websocket, f"면접 진행 중 오류 발생: {str(e)}")
    finally:
        db.close()
        if websocket.state == WebSocketState.CONNECTED:
            await websocket.close()

# --- 헬퍼 함수: 면접 초기화 ---
async def _initialize_interview(db: Session, interview_id: int, websocket: WebSocket):
    """면접 세션, 지원자, 페르소나 로드 및 상태 업데이트"""
    session = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
    if not session:
        await _safe_send_error(websocket, f"면접 세션 {interview_id}를 찾을 수 없습니다.")
        return None, None, None

    applicant = db.query(Applicant).filter(Applicant.id == session.applicant_id).first()
    # 페르소나 로드 (예시: DB 또는 설정 파일에서 로드)
    # 실제로는 session.job_ids 등을 기반으로 관련 페르소나를 로드해야 함
    personas = db.query(Persona).limit(3).all() # 예시로 3개 로드
    if not personas or len(personas) < 3: # 페르소나가 충분하지 않으면 에러 처리
         await _safe_send_error(websocket, f"면접에 필요한 페르소나를 로드할 수 없습니다.")
         return None, None, None

    # 상태 업데이트
    session.status = InterviewStatus.IN_PROGRESS
    session.started_at = datetime.utcnow()
    db.commit()
    print(f"Service: 면접 세션 {interview_id} 시작됨.")
    return session, applicant, personas

# --- 헬퍼 함수: 면접 결과 저장 ---
async def _save_interview_result(db: Session, interview_id: int, question: str, answer: str, q_type: str, persona_id: Optional[int]):
    """면접 질문/답변 결과를 DB에 저장"""
    try:
        result = InterviewResult(
            interview_id=interview_id,
            question_text=question,
            question_type=q_type,
            is_common=(q_type == "common"),
            persona_id=persona_id, # 어떤 페르소나가 질문했는지 기록
            stt_full_text=answer,
            created_at=datetime.utcnow()
        )
        db.add(result)
        db.commit()
        print(f"DB: 질문 '{question[:20]}...'에 대한 답변 저장됨.")
    except Exception as e:
        db.rollback()
        print(f"DB 저장 에러: {e}")
        # 필요 시 에러 전파

# --- 헬퍼 함수: 면접 종료 처리 ---
async def _finalize_interview(db: Session, interview_id: int, websocket: WebSocket, manager: InterviewFlowManager):
    """면접 세션 완료 처리 및 최종 메시지 전송"""
    final_message = "수고하셨습니다. 면접이 종료되었습니다."
    final_comments = manager.generate_final_comments() # 최종 코멘트 생성 시도

    # 코멘트 포함 메시지 구성 (선택 사항)
    comment_texts = [f"{p.display_name}: {c}" for p, c in zip(manager.personas, final_comments.values())]
    full_final_message = f"{final_message}\n\n[면접관 코멘트]\n" + "\n".join(comment_texts)

    await _send_tts_audio(websocket, final_message) # 종료 메시지는 간단하게

    session = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
    if session:
        session.status = InterviewStatus.COMPLETED
        session.completed_at = datetime.utcnow()
        # 최종 코멘트 저장 (예: session 테이블의 comments 필드)
        # session.comments = json.dumps(final_comments) # JSON 문자열로 저장
        db.commit()

    await websocket.send_json({
        "type": "interview_done",
        "message": full_final_message, # 코멘트 포함한 메시지
        "interview_id": interview_id
    })
    print(f"Service: 면접 세션 {interview_id} 완료 처리됨.")

# --- 헬퍼 함수: 세션 상태 업데이트 ---
async def _update_session_status(db: Session, interview_id: int, status: InterviewStatus):
    """면접 세션 상태 업데이트 (에러 발생 시)"""
    try:
        session = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
        if session and session.status != InterviewStatus.COMPLETED: # 완료된 세션은 건드리지 않음
            session.status = status
            db.commit()
            print(f"DB: 면접 세션 {interview_id} 상태를 {status.value}(으)로 업데이트.")
    except Exception as e:
        db.rollback()
        print(f"DB 상태 업데이트 에러: {e}")

# --- 헬퍼 함수: 안전한 에러 메시지 전송 ---
async def _safe_send_error(websocket: WebSocket, message: str):
    """WebSocket 연결 상태 확인 후 에러 메시지 전송"""
    if websocket.state == WebSocketState.CONNECTED:
        await websocket.send_json({"type": "error", "message": message})


# --- 기존 TTS / STT 헬퍼 함수들 ---
# (_send_tts_audio, _get_stt_answer, stream_text_to_speech 등은 이전 코드와 동일하게 유지)

# --- 3. 헬퍼 함수: TTS (OpenAI) ---

async def stream_text_to_speech(text_to_speak: str, websocket: WebSocket):
    """
    OpenAI TTS를 사용하여 텍스트를 음성으로 변환하고 WebSocket을 통해 실시간 스트리밍합니다.

    Args:
        text_to_speak: 음성으로 변환할 텍스트
        websocket: 클라이언트와 연결된 WebSocket 객체
    """
    try:
        print(f"OpenAI TTS 스트리밍 시작: {text_to_speak[:50]}...")

        # OpenAI TTS API 호출 (동기 작업을 비동기로 실행)
        def generate_speech():
            response = openai_client.audio.speech.create(
                model="tts-1",  # tts-1-hd for higher quality
                voice="nova",   # alloy, echo, fable, onyx, nova, shimmer
                input=text_to_speak,
                response_format="mp3" # 또는 opus 등 streaming 친화적 포맷
            )
            return response

        response = await asyncio.to_thread(generate_speech)

        # 스트리밍 응답을 청크 단위로 읽기 및 전송
        chunk_size = 1024  # 1KB 청크

        # OpenAI response는 이미 bytes 형태이므로 chunk로 나눠서 전송
        # response.content 대신 response.iter_bytes() 사용 가능성 확인 (streaming 지원 시)
        audio_bytes = response.content # .content는 전체를 로드할 수 있음. 대용량 주의

        # 청크 단위로 전송
        for i in range(0, len(audio_bytes), chunk_size):
            chunk = audio_bytes[i:i + chunk_size]
            if websocket.state == WebSocketState.CONNECTED:
                await websocket.send_bytes(chunk)
            else:
                print("TTS 전송 중단: WebSocket 연결 끊김.")
                break

        print(f"OpenAI TTS 스트리밍 완료: {text_to_speak[:50]}...")

    except Exception as e:
        print(f"OpenAI TTS 에러: {e}")
        await _safe_send_error(websocket, f"TTS 생성 중 오류 발생: {str(e)}")


async def _send_tts_audio(websocket: WebSocket, text: str):
    """텍스트를 TTS로 변환하고 WebSocket으로 스트리밍 전송"""
    print(f"TTS 전송 시작: {text[:20]}...")
    await websocket.send_json({"type": "question_start", "text": text})
    await stream_text_to_speech(text, websocket) # OpenAI TTS 함수 호출
    await websocket.send_json({"type": "question_end"})
    print(f"TTS 전송 완료: {text[:20]}...")


# --- 4. 헬퍼 함수: STT (OpenAI Whisper) ---

async def _get_stt_answer(websocket: WebSocket, session_id: str, index: int) -> str:
    """클라이언트 오디오를 받아 Whisper로 텍스트 변환"""
    print("STT: 답변 수신 대기 중...")
    audio_buffer = bytearray()

    while True:
        try:
            message = await websocket.receive()
            if "bytes" in message:
                audio_buffer.extend(message["bytes"])
            if "text" in message:
                data = json.loads(message["text"])
                if data.get("type") == "answer_done":
                    print("STT: 답변 녹음 완료. (총 {} bytes)".format(len(audio_buffer)))
                    break
        except WebSocketDisconnect:
             print("STT 수신 중 WebSocket 연결 끊김.")
             return "(연결 끊김으로 답변 수신 실패)" # 또는 예외 발생

    if not audio_buffer:
        return ""

    await websocket.send_json({"type": "transcribing_start"})

    try:
        audio_file = io.BytesIO(bytes(audio_buffer))
        # 클라이언트 포맷에 따라 파일 이름/확장자 지정 (Whisper가 추측하도록)
        audio_file.name = f"interview_{session_id}_q{index}.webm" # 예시

        def transcribe_audio():
            result = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="ko",
                response_format="json"
            )
            return result.text

        text_answer = await asyncio.to_thread(transcribe_audio)
        print(f"STT: 변환 완료 - {text_answer[:50]}...")
        return text_answer

    except Exception as e:
        print(f"STT 에러: {e}")
        await _safe_send_error(websocket, f"STT 변환 중 오류 발생: {str(e)}")
        return "답변 인식에 실패했습니다."


# --- 5. 헬퍼 함수: LLM (Bedrock - InterviewFlowManager가 처리) ---
# _generate_follow_up_question 함수는 InterviewFlowManager 내부 로직을 사용하므로 제거 가능
# (만약 필요하다면 FlowManager의 인스턴스를 통해 호출)