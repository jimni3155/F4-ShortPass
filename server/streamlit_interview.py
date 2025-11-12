"""
3-Way AI 면접 시뮬레이터 (Streamlit)

3개 기업의 PDF를 파싱하여 3명의 면접관 페르소나를 생성하고,
공통 질문 → 분기 질문 플로우로 면접을 진행합니다.
"""

import streamlit as st
import os
import sys

# 프로젝트 루트를 Python path에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.pdf_parser import PDFParser
from services.persona_generator import PersonaGenerator
from services.interview_flow_manager import InterviewFlowManager, InterviewStage


# Streamlit 페이지 설정
st.set_page_config(
    page_title="AI 3-Way 면접 시뮬레이터",
    page_icon="🎤",
    layout="wide"
)


def initialize_session_state():
    """세션 상태 초기화"""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False
        st.session_state.company_profiles = []
        st.session_state.personas = []
        st.session_state.flow_manager = None
        st.session_state.interview_started = False
        st.session_state.chat_history = []  # UI용 채팅 히스토리
        st.session_state.current_question = None
        st.session_state.current_persona = None  # 현재 질문 중인 페르소나


def load_pdfs_and_create_personas():
    """PDF 로드 및 페르소나 생성"""
    pdf_dir = "docs"

    with st.spinner("📄 PDF 파일 분석 중..."):
        # PDF 파싱
        parser = PDFParser()
        profiles = parser.parse_all_pdfs(pdf_dir)

        if not profiles:
            st.error("PDF 파일을 찾을 수 없습니다!")
            return False

        st.session_state.company_profiles = profiles

    with st.spinner("🎭 면접관 페르소나 생성 중..."):
        # 페르소나 생성
        generator = PersonaGenerator()
        personas = generator.create_personas_from_profiles(profiles)

        if not personas:
            st.error("페르소나 생성 실패!")
            return False

        st.session_state.personas = personas

    st.session_state.initialized = True
    return True


def start_interview(applicant_name: str):
    """면접 시작"""
    # FlowManager 초기화
    st.session_state.flow_manager = InterviewFlowManager(
        personas=st.session_state.personas,
        applicant_name=applicant_name
    )

    st.session_state.interview_started = True
    st.session_state.chat_history = []

    # 첫 번째 공통 질문
    first_question = st.session_state.flow_manager.get_next_common_question()
    st.session_state.current_question = first_question
    st.session_state.current_persona = None  # 공통 질문은 페르소나 없음

    # 채팅 히스토리에 추가
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": f"💬 면접관 (공통): {first_question}",
        "persona": None
    })


def process_answer(answer: str):
    """답변 처리 및 다음 질문 생성"""
    flow = st.session_state.flow_manager

    # 채팅 히스토리에 답변 추가
    st.session_state.chat_history.append({
        "role": "user",
        "content": answer
    })

    # 현재 단계에 따라 처리
    if flow.stage == InterviewStage.COMMON:
        # 공통 질문 단계
        flow.add_common_qa(st.session_state.current_question, answer)

        # 다음 공통 질문
        next_question = flow.get_next_common_question()

        if next_question:
            # 아직 공통 질문이 남음
            st.session_state.current_question = next_question
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"💬 면접관 (공통): {next_question}",
                "persona": None
            })
        else:
            # 공통 질문 종료 → 분기 단계 시작
            flow.start_branched_stage()

            # 3명의 면접관이 동시에 첫 질문
            st.session_state.chat_history.append({
                "role": "system",
                "content": "🎯 **이제 3개 기업의 면접관이 각각 질문합니다!**"
            })

            for persona in st.session_state.personas:
                # 각 페르소나의 첫 질문
                question = persona.welcome_message
                flow.conversation_histories[persona.persona_id].append({
                    "role": "assistant",
                    "content": question
                })

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"**{persona.display_name}**: {question}",
                    "persona": persona
                })

            # 첫 번째 페르소나의 질문으로 시작
            st.session_state.current_persona = st.session_state.personas[0]

    elif flow.stage == InterviewStage.BRANCHED:
        # 분기 질문 단계
        current_persona = st.session_state.current_persona

        # 답변 처리 및 꼬리 질문 생성
        next_question = flow.process_branched_answer(current_persona, answer)

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": f"**{current_persona.display_name}**: {next_question}",
            "persona": current_persona
        })

        # 다음 페르소나로 순환
        current_idx = st.session_state.personas.index(current_persona)
        next_idx = (current_idx + 1) % len(st.session_state.personas)
        st.session_state.current_persona = st.session_state.personas[next_idx]

        # 면접 종료 체크
        if flow.should_finish_interview():
            flow.finish_interview()

            # 최종 코멘트
            comments = flow.generate_final_comments()

            st.session_state.chat_history.append({
                "role": "system",
                "content": "✅ **면접이 종료되었습니다! 각 면접관의 코멘트:**"
            })

            for persona in st.session_state.personas:
                comment = comments.get(persona.persona_id, "감사합니다.")
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"**{persona.display_name}**: {comment}",
                    "persona": persona
                })

            st.session_state.chat_history.append({
                "role": "system",
                "content": "🎉 **수고하셨습니다!**"
            })


def main():
    """메인 앱"""
    st.title("🎤 AI 3-Way 면접 시뮬레이터")
    st.markdown("---")

    initialize_session_state()

    # 사이드바: 시스템 정보
    with st.sidebar:
        st.header("📊 시스템 정보")

        if not st.session_state.initialized:
            if st.button("🚀 PDF 로드 및 페르소나 생성", type="primary"):
                success = load_pdfs_and_create_personas()
                if success:
                    st.success("✅ 초기화 완료!")
                    st.rerun()
        else:
            st.success(f"✅ {len(st.session_state.company_profiles)}개 기업 로드됨")
            st.success(f"✅ {len(st.session_state.personas)}명의 면접관 준비됨")

            # 페르소나 정보
            st.subheader("🎭 면접관 정보")
            for persona in st.session_state.personas:
                with st.expander(persona.display_name):
                    st.write(f"**기업**: {persona.company_name}")
                    st.write(f"**스타일**: {persona.style_description}")
                    st.write(f"**키워드**: {', '.join(persona.focus_keywords)}")

    # 메인 화면
    if not st.session_state.initialized:
        st.info("👈 왼쪽 사이드바에서 'PDF 로드 및 페르소나 생성' 버튼을 눌러주세요.")
        return

    if not st.session_state.interview_started:
        # 면접 시작 전
        st.subheader("📝 지원자 정보 입력")

        col1, col2 = st.columns(2)

        with col1:
            applicant_name = st.text_input("이름", placeholder="홍길동")

        with col2:
            applicant_field = st.text_input("지원 분야", placeholder="백엔드 개발")

        st.markdown("---")

        if st.button("🎬 면접 시작하기", type="primary", disabled=not applicant_name):
            start_interview(applicant_name)
            st.rerun()

    else:
        # 면접 진행 중
        flow = st.session_state.flow_manager

        # 현재 단계 표시
        if flow.stage == InterviewStage.COMMON:
            st.info(f"📌 현재 단계: 공통 질문 ({flow.common_question_index}/{len(flow.COMMON_QUESTIONS)})")
        elif flow.stage == InterviewStage.BRANCHED:
            st.info(f"📌 현재 단계: 기업별 특화 질문 (진행 중)")
        else:
            st.success("✅ 면접 종료")

        # 채팅 히스토리 표시
        st.subheader("💬 면접 진행")

        chat_container = st.container()

        with chat_container:
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    st.chat_message("user").write(msg["content"])
                elif msg["role"] == "assistant":
                    with st.chat_message("assistant"):
                        st.write(msg["content"])
                elif msg["role"] == "system":
                    st.info(msg["content"])

        # 답변 입력 (면접 종료 전까지)
        if flow.stage != InterviewStage.FINISHED:
            with st.form(key="answer_form", clear_on_submit=True):
                user_answer = st.text_area(
                    "📝 답변 입력",
                    placeholder="답변을 입력하세요...",
                    height=100
                )

                submit = st.form_submit_button("답변 제출", type="primary")

                if submit and user_answer.strip():
                    process_answer(user_answer.strip())
                    st.rerun()

        else:
            # 면접 종료 후
            if st.button("🔄 새로운 면접 시작"):
                # 세션 초기화
                st.session_state.interview_started = False
                st.session_state.chat_history = []
                st.session_state.flow_manager = None
                st.rerun()


if __name__ == "__main__":
    main()
