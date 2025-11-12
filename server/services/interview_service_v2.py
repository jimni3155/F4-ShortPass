# server/services/interview_service_v2.py
"""
면접 진행 서비스 V2 (WebSocket 기반, 순차 페르소나 방식)
- 1개 회사의 여러 페르소나가 순차적으로 질문 (기술형 → 논리형 → 컬처핏형)
- TTS: OpenAI TTS
- STT: OpenAI Whisper
"""

import boto3
import json
import asyncio
import io
from fastapi import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState
from openai import OpenAI
from core.config import *
from db.database import SessionLocal
from models.interview import (
    InterviewSession, InterviewStatus, InterviewResult,
    Applicant, PersonaInstance, SessionPersona, SessionTranscript,
    SessionScore, SessionExplanation
)
from datetime import datetime
from sqlalchemy.orm import Session
from typing import Optional, List

# OpenAI 클라이언트
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Bedrock 클라이언트
bedrock_runtime = boto3.client('bedrock-runtime', region_name=AWS_REGION)


# ==================== 메인 핸들러 ====================

async def handle_interview_session(websocket: WebSocket, interview_id: int):
    """
    WebSocket을 통한 면접 세션 핸들러 (순차 페르소나 방식)
    """
    print(f"Service: 면접 세션 핸들러 시작 (interview_id={interview_id})")

    db = SessionLocal()
    turn_counter = 0

    try:
        # 1. 면접 세션 로드
        session = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
        if not session:
            await _safe_send_error(websocket, f"면접 세션 {interview_id}를 찾을 수 없습니다.")
            return

        applicant = db.query(Applicant).filter(Applicant.id == session.applicant_id).first()
        applicant_name = applicant.name if applicant else "지원자"

        # 2. 세션 페르소나 로드 (순차 패널)
        session_personas = (
            db.query(SessionPersona)
            .filter(SessionPersona.session_id == interview_id)
            .order_by(SessionPersona.order)
            .all()
        )

        if not session_personas:
            await _safe_send_error(websocket, "세션에 페르소나가 설정되지 않았습니다.")
            return

        # PersonaInstance 로드
        persona_instances = []
        for sp in session_personas:
            pi = db.query(PersonaInstance).filter(PersonaInstance.id == sp.persona_instance_id).first()
            if pi:
                persona_instances.append(pi)

        if not persona_instances:
            await _safe_send_error(websocket, "페르소나 인스턴스를 로드할 수 없습니다.")
            return

        # 3. 세션 상태 업데이트
        session.status = InterviewStatus.IN_PROGRESS
        session.started_at = datetime.utcnow()
        db.commit()

        # 4. 공통 질문 단계 (간단한 자기소개)
        common_questions = [
            "먼저 간단히 자기소개 부탁드립니다.",
            "지원 동기를 말씀해주세요."
        ]

        for common_q in common_questions:
            await _send_tts_audio(websocket, common_q)
            answer = await _get_stt_answer(websocket, str(interview_id), turn_counter)
            if not answer:
                answer = "(답변이 없습니다.)"

            await websocket.send_json({"type": "answer_text", "text": answer})

            # 대화 기록 저장
            await _save_transcript(db, interview_id, None, turn_counter, f"Q: {common_q}", {})
            turn_counter += 1
            await _save_transcript(db, interview_id, None, turn_counter, f"A: {answer}", {})
            turn_counter += 1

        # 5. 페르소나별 순차 질문 (라운드 로빈)
        await websocket.send_json({"type": "stage_change", "stage": "persona_rounds"})

        max_rounds_per_persona = 3
        for round_num in range(max_rounds_per_persona):
            for persona_instance in persona_instances:
                # 페르소나 정보 전송
                await websocket.send_json({
                    "type": "persona_turn",
                    "persona_name": persona_instance.instance_name,
                    "round": round_num + 1
                })

                # 질문 생성
                await websocket.send_json({"type": "generating_question"})
                question = await _generate_persona_question(
                    db, interview_id, persona_instance, applicant_name
                )

                # 질문 전송 (TTS)
                await _send_tts_audio(websocket, question)

                # 답변 수신 (STT)
                answer = await _get_stt_answer(websocket, str(interview_id), turn_counter)
                if not answer:
                    answer = "(답변이 없습니다.)"

                await websocket.send_json({"type": "answer_text", "text": answer})

                # 대화 기록 저장
                await _save_transcript(
                    db, interview_id, persona_instance.id, turn_counter,
                    f"Q: {question}", {"persona_name": persona_instance.instance_name}
                )
                turn_counter += 1
                await _save_transcript(
                    db, interview_id, persona_instance.id, turn_counter,
                    f"A: {answer}", {"persona_name": persona_instance.instance_name}
                )
                turn_counter += 1

                # 평가 점수 저장 (더미)
                await _save_score(db, interview_id, persona_instance.id, "technical_depth", 85.0)
                await _save_score(db, interview_id, persona_instance.id, "communication", 88.0)

                # 평가 근거 저장 (더미)
                await _save_explanation(
                    db, interview_id, persona_instance.id, "technical_depth",
                    "기술적 이해도가 높음", {"coherence": 0.91, "evidence_match": 0.84}
                )

        # 6. 면접 종료
        await _finalize_interview(db, interview_id, websocket)

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


# ==================== 헬퍼 함수 ====================

async def _generate_persona_question(
    db: Session,
    interview_id: int,
    persona_instance: PersonaInstance,
    applicant_name: str
) -> str:
    """
    페르소나 기반 질문 생성 (LLM 사용)
    """
    try:
        # 이전 대화 기록 로드
        transcripts = (
            db.query(SessionTranscript)
            .filter(SessionTranscript.session_id == interview_id)
            .filter(SessionTranscript.persona_instance_id == persona_instance.id)
            .order_by(SessionTranscript.turn)
            .all()
        )

        history_text = "\n".join([t.text for t in transcripts]) if transcripts else "(없음)"

        # 프롬프트 구성
        prompt = f"""당신은 {persona_instance.instance_name} 면접관입니다.

이전 대화:
{history_text}

지원자({applicant_name})에게 {persona_instance.instance_name} 관점에서 다음 질문을 생성하세요.
질문만 생성하고 다른 설명은 붙이지 마세요."""

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 256,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        })

        response = bedrock_runtime.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=body,
            contentType="application/json",
            accept="application/json"
        )

        response_body = json.loads(response['body'].read().decode('utf-8'))
        question = response_body['content'][0]['text'].strip()

        return question

    except Exception as e:
        print(f"질문 생성 에러: {e}")
        return f"{persona_instance.instance_name} 관점에서 경험을 설명해주세요."


async def _save_transcript(
    db: Session,
    session_id: int,
    persona_instance_id: Optional[int],
    turn: int,
    text: str,
    meta_json: dict
):
    """대화 기록 저장"""
    try:
        transcript = SessionTranscript(
            session_id=session_id,
            persona_instance_id=persona_instance_id,
            turn=turn,
            text=text,
            meta_json=meta_json,
            created_at=datetime.utcnow()
        )
        db.add(transcript)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Transcript 저장 에러: {e}")


async def _save_score(
    db: Session,
    session_id: int,
    persona_instance_id: int,
    criterion_key: str,
    score: float
):
    """평가 점수 저장"""
    try:
        score_record = SessionScore(
            session_id=session_id,
            persona_instance_id=persona_instance_id,
            criterion_key=criterion_key,
            score=score,
            created_at=datetime.utcnow()
        )
        db.add(score_record)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Score 저장 에러: {e}")


async def _save_explanation(
    db: Session,
    session_id: int,
    persona_instance_id: int,
    criterion_key: str,
    explanation: str,
    log_json: dict
):
    """평가 근거 저장"""
    try:
        expl = SessionExplanation(
            session_id=session_id,
            persona_instance_id=persona_instance_id,
            criterion_key=criterion_key,
            explanation=explanation,
            log_json=log_json,
            created_at=datetime.utcnow()
        )
        db.add(expl)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Explanation 저장 에러: {e}")


async def _finalize_interview(db: Session, interview_id: int, websocket: WebSocket):
    """면접 종료 처리"""
    final_message = "수고하셨습니다. 면접이 종료되었습니다."
    await _send_tts_audio(websocket, final_message)

    session = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
    if session:
        session.status = InterviewStatus.COMPLETED
        session.completed_at = datetime.utcnow()
        db.commit()

    await websocket.send_json({
        "type": "interview_done",
        "message": final_message,
        "interview_id": interview_id
    })
    print(f"Service: 면접 세션 {interview_id} 완료.")


async def _update_session_status(db: Session, interview_id: int, status: InterviewStatus):
    """세션 상태 업데이트"""
    try:
        session = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
        if session and session.status != InterviewStatus.COMPLETED:
            session.status = status
            db.commit()
    except Exception as e:
        db.rollback()
        print(f"상태 업데이트 에러: {e}")


async def _safe_send_error(websocket: WebSocket, message: str):
    """안전한 에러 메시지 전송"""
    if websocket.state == WebSocketState.CONNECTED:
        await websocket.send_json({"type": "error", "message": message})


# ==================== TTS / STT ====================

async def stream_text_to_speech(text_to_speak: str, websocket: WebSocket):
    """OpenAI TTS 스트리밍"""
    try:
        print(f"OpenAI TTS 스트리밍 시작: {text_to_speak[:50]}...")

        def generate_speech():
            response = openai_client.audio.speech.create(
                model="tts-1",
                voice="nova",
                input=text_to_speak,
                response_format="mp3"
            )
            return response

        response = await asyncio.to_thread(generate_speech)
        audio_bytes = response.content
        chunk_size = 1024

        for i in range(0, len(audio_bytes), chunk_size):
            chunk = audio_bytes[i:i + chunk_size]
            if websocket.state == WebSocketState.CONNECTED:
                await websocket.send_bytes(chunk)
            else:
                print("TTS 전송 중단: WebSocket 연결 끊김.")
                break

        print(f"OpenAI TTS 스트리밍 완료.")

    except Exception as e:
        print(f"OpenAI TTS 에러: {e}")
        await _safe_send_error(websocket, f"TTS 생성 중 오류 발생: {str(e)}")


async def _send_tts_audio(websocket: WebSocket, text: str):
    """TTS 전송"""
    print(f"TTS 전송 시작: {text[:20]}...")
    await websocket.send_json({"type": "question_start", "text": text})
    await stream_text_to_speech(text, websocket)
    await websocket.send_json({"type": "question_end"})
    print(f"TTS 전송 완료.")


async def _get_stt_answer(websocket: WebSocket, session_id: str, index: int) -> str:
    """STT 답변 수신"""
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
                    print(f"STT: 답변 녹음 완료 ({len(audio_buffer)} bytes)")
                    break
        except WebSocketDisconnect:
            print("STT 수신 중 연결 끊김.")
            return "(연결 끊김으로 답변 수신 실패)"

    if not audio_buffer:
        return ""

    await websocket.send_json({"type": "transcribing_start"})

    try:
        audio_file = io.BytesIO(bytes(audio_buffer))
        audio_file.name = f"interview_{session_id}_q{index}.webm"

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
