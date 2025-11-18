# ai/services/evaluation_service.py
"""
평가 실행 서비스 (LangGraph 연결)
"""

from typing import Dict, Any
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session

from ai.agents.evaluation_graph import run_evaluation
from ai.agents.state import EvaluationState
from ai.agents.rag_agent import RAGAgent
from ai.utils.llm_client import LLMClient
from db.session import get_db_session
from models.evaluation import CompetencyEvaluation, EvaluationLog
from models.interview import InterviewSession, InterviewResult, SessionTranscript
from models.job import Job
from models.applicant import Applicant


class EvaluationService:
    """
    평가 실행 서비스
    """
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.rag_agent = RAGAgent(llm_client)
    
    async def create_pending_evaluation(
        self,
        db: Session,
        interview_id: int,
        job_id: int
    ) -> int:
        """
        평가 레코드 먼저 생성 (상태: pending)
        """
        evaluation = CompetencyEvaluation(
            interview_id=interview_id,
            job_id=job_id,
            evaluation_status="pending",
            created_at=datetime.now()
        )
        
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        
        return evaluation.id
    
    async def run_evaluation_for_application(
        self,
        interview_id: int,
        job_id: int,
        evaluation_id: int
    ) -> Dict[str, Any]:
        """
        실제 평가 실행 (백그라운드)
        """
        async with get_db_session() as db:
            try:
                # 상태 업데이트: pending → evaluating
                evaluation = await db.get(CompetencyEvaluation, evaluation_id)
                evaluation.evaluation_status = "evaluating"
                evaluation.started_at = datetime.now()
                await db.commit()
                
                # 1. 데이터 로드
                interview = await db.get(InterviewSession, interview_id)
                job = await db.get(Job, job_id)
                applicant = await db.get(Applicant, interview.applicant_id)
                
                if not all([interview, job, applicant]):
                    raise ValueError("Required data not found")
                
                # 2. Initial State 구성
                initial_state = await self._build_initial_state(
                    db=db,
                    interview=interview,
                    job=job,
                    applicant=applicant
                )
                
                # 3. LangGraph 실행
                final_state = await run_evaluation(self.llm_client, initial_state)
                
                # 4. DB 저장
                await self._save_evaluation_results(db, evaluation, final_state)
                
                return {
                    "evaluation_id": evaluation.id,
                    "status": "completed",
                    "error_message": None
                }
                
            except Exception as e:
                # 실패 처리
                evaluation.evaluation_status = "failed"
                evaluation.error_message = str(e)
                evaluation.completed_at = datetime.now()
                await db.commit()
                raise
    
    async def _build_initial_state(
        self,
        db: Session,
        interview: InterviewSession,
        job: Job,
        applicant: Applicant
    ) -> EvaluationState:
        """
        LangGraph Initial State 구성
        RAG Agent를 사용하여 JD 파싱
        """
        # 면접 대화록
        transcript = await self._build_transcript(db, interview.id)

        # 평가 기준표
        standards = await self._load_evaluation_standards()

        # RAG Agent로 JD 파싱 (필드가 비어있으면)
        if not job.required_skills or not job.dynamic_evaluation_criteria:
            print(f"RAG Agent: JD 파싱 시작 (job_id={job.id})")
            parsed_data = await self.rag_agent.parse_jd(
                job_description=job.description or "",
                job_title=job.title
            )

            # Job 테이블 업데이트
            job.required_skills = parsed_data["required_skills"]
            job.preferred_skills = parsed_data["preferred_skills"]
            job.domain_requirements = parsed_data["domain_requirements"]
            job.dynamic_evaluation_criteria = parsed_data["dynamic_evaluation_criteria"]
            job.competency_weights = parsed_data["competency_weights"]
            job.position_type = parsed_data["position_type"]
            job.seniority_level = parsed_data["seniority_level"]
            job.main_responsibilities = parsed_data["main_responsibilities"]

            db.commit()
            db.refresh(job)
            print(f"RAG Agent: JD 파싱 완료 - 필수 기술 {len(job.required_skills)}개, 평가 기준 {len(job.dynamic_evaluation_criteria)}개")

            # 면접 대화록 (문자열)
            interview_transcript_str = await self._build_transcript_string(db, interview.id)

            # 면접 대화록 (구조화된 JSON)
            structured_transcript_list = await self._build_structured_transcript(db, interview.id)

            # 평가 기준표
            standards = await self._load_evaluation_standards()

            # RAG Agent로 JD 파싱 (필드가 비어있으면)
            if not job.required_skills or not job.dynamic_evaluation_criteria:
                print(f"RAG Agent: JD 파싱 시작 (job_id={job.id})")
                parsed_data = await self.rag_agent.parse_jd(
                    job_description=job.description or "",
                    job_title=job.title
                )

                # Job 테이블 업데이트
                job.required_skills = parsed_data["required_skills"]
                job.preferred_skills = parsed_data["preferred_skills"]
                job.domain_requirements = parsed_data["domain_requirements"]
                job.dynamic_evaluation_criteria = parsed_data["dynamic_evaluation_criteria"]
                job.competency_weights = parsed_data["competency_weights"]
                job.position_type = parsed_data["position_type"]
                job.seniority_level = parsed_data["seniority_level"]
                job.main_responsibilities = parsed_data["main_responsibilities"]

                db.commit()
                db.refresh(job)
                print(f"RAG Agent: JD 파싱 완료 - 필수 기술 {len(job.required_skills)}개, 평가 기준 {len(job.dynamic_evaluation_criteria)}개")

            return {
                "application_id": f"{interview.id}-{job.id}",
                "interview_id": interview.id,
                "job_id": job.id,

                # 면접 데이터
                "interview_transcript": interview_transcript_str,
                "structured_transcript": structured_transcript_list,
                "applicant_resume": applicant.resume_parsed_data or {},
                "applicant_portfolio": applicant.portfolio_parsed_data or {},
                "applicant_skills": applicant.skills or [],
                "applicant_experience_years": applicant.total_experience_years or 0,

                # Job 데이터 (RAG Agent 파싱 결과)
                "job_description": job.description or "",
                "job_title": job.title,
                "required_skills": job.required_skills or [],
                "preferred_skills": job.preferred_skills or [],
                "domain_requirements": job.domain_requirements or [],
                "dynamic_evaluation_criteria": job.dynamic_evaluation_criteria or [],
                "competency_weights": job.competency_weights or self._default_weights(),

                # 평가 기준표
                "evaluation_standards": standards,

                # 초기값
                "job_expertise_result": None,
                "analytical_result": None,
                "execution_result": None,
                "relationship_result": None,
                "resilience_result": None,
                "influence_result": None,
                "aggregated_scores": None,
                "overall_feedback": None,
                "key_insights": None,
                "hiring_recommendation": None,
                "recommendation_reasoning": None,
                "job_requirement_fit_score": None,
                "fit_analysis": None,
                "expected_onboarding_duration": None,
                "onboarding_support_needed": None,

                # 메타
                "evaluation_status": "evaluating",
                "error_message": None,
                "started_at": datetime.now(),
                "completed_at": None,
                "execution_logs": [],
            }

    
    async def _save_evaluation_results(
        self,
        db: Session,
        evaluation: CompetencyEvaluation,
        final_state: EvaluationState
    ):
        """
        평가 결과를 DB에 저장
        """
        evaluation.evaluation_status = "completed"
        evaluation.completed_at = datetime.now()
        
        # 6개 역량 결과
        evaluation.job_expertise = final_state.get("job_expertise_result")
        evaluation.analytical = final_state.get("analytical_result")
        evaluation.execution = final_state.get("execution_result")
        evaluation.relationship = final_state.get("relationship_result")
        evaluation.resilience = final_state.get("resilience_result")
        evaluation.influence = final_state.get("influence_result")
        
        # 통합 결과
        evaluation.overall_feedback = final_state.get("overall_feedback")
        evaluation.key_insights = final_state.get("key_insights")
        evaluation.hiring_recommendation = final_state.get("hiring_recommendation")
        evaluation.recommendation_reasoning = final_state.get("recommendation_reasoning")
        evaluation.job_requirement_fit_score = final_state.get("job_requirement_fit_score")
        evaluation.fit_analysis = final_state.get("fit_analysis")
        evaluation.expected_onboarding_duration = final_state.get("expected_onboarding_duration")
        evaluation.onboarding_support_needed = final_state.get("onboarding_support_needed")

        # reasoning_log 데이터 구성 및 저장
        reasoning_log_data = {}
        structured_transcript = final_state.get("structured_transcript", [])
        
        competency_keys = [
            "job_expertise", "analytical", "execution",
            "relationship", "resilience", "influence"
        ]

        for key in competency_keys:
            result_key = f"{key}_result"
            competency_result = final_state.get(result_key)
            if competency_result:
                # LLM이 생성한 evidence를 structured_transcript 정보로 보강
                if "evidence" in competency_result and structured_transcript:
                    competency_result["evidence"] = self._enrich_evidence_with_transcript_info(
                        competency_result["evidence"],
                        structured_transcript
                    )
                reasoning_log_data[key] = competency_result
        
        evaluation.reasoning_log = reasoning_log_data
        
        await db.commit()
        
        # 로그 저장
        for log in final_state.get("execution_logs", []):
            eval_log = EvaluationLog(
                competency_evaluation_id=evaluation.id,
                log_type="evaluator" if "evaluator" in log["node"] else "aggregator",
                agent_name=log["node"],
                execution_time_ms=int(log["execution_time"] * 1000),
                error_occurred=log["error"] is not None,
                error_message=log["error"],
            )
            db.add(eval_log)
        
        await db.commit()
    
    async def _build_transcript_string(self, db: Session, interview_id: int) -> str:
        """면접 대화록 생성"""
        stmt = select(InterviewResult).where(
            InterviewResult.interview_id == interview_id
        ).order_by(InterviewResult.id)
        
        results = (await db.execute(stmt)).scalars().all()
        
        transcript_lines = []
        for i, result in enumerate(results, 1):
            transcript_lines.append(f"Turn {i}:")
            transcript_lines.append(f"Q: {result.question_text}")
            transcript_lines.append(f"A: {result.stt_full_text}")
            transcript_lines.append("")
        
        return "\n".join(transcript_lines)

    async def _build_structured_transcript(self, db: Session, interview_id: int) -> List[Dict[str, Any]]:
        """
        구조화된 면접 대화록 생성 (SessionTranscript 우선, 없으면 InterviewResult 사용)
        """
        structured_transcript = []

        # 1. SessionTranscript 조회 시도
        stmt_st = select(SessionTranscript).where(
            SessionTranscript.session_id == interview_id
        ).order_by(SessionTranscript.turn)
        session_transcripts = (await db.execute(stmt_st)).scalars().all()

        if session_transcripts:
            for st in session_transcripts:
                utterance = {
                    "id": st.turn,
                    "speaker": st.meta_json.get("speaker", "Unknown") if st.meta_json else "Unknown",
                    "text": st.text,
                    "start_time": st.meta_json.get("start_time") if st.meta_json else None,
                    "end_time": st.meta_json.get("end_time") if st.meta_json else None,
                }
                structured_transcript.append(utterance)
        else:
            # 2. SessionTranscript가 없으면 InterviewResult 사용 (타임스탬프 없음)
            stmt_ir = select(InterviewResult).where(
                InterviewResult.interview_id == interview_id
            ).order_by(InterviewResult.id)
            interview_results = (await db.execute(stmt_ir)).scalars().all()

            turn_id_counter = 1
            for result in interview_results:
                # 질문
                structured_transcript.append({
                    "id": turn_id_counter,
                    "speaker": "Interviewer",
                    "text": result.question_text,
                    "start_time": None,
                    "end_time": None,
                })
                turn_id_counter += 1
                # 답변
                structured_transcript.append({
                    "id": turn_id_counter,
                    "speaker": "Applicant",
                    "text": result.stt_full_text,
                    "start_time": None,
                    "end_time": None,
                })
                turn_id_counter += 1
        
        return structured_transcript
    
    async def _load_evaluation_standards(self) -> str:
        """평가 기준표 로드"""
        return """
        90-100: 상위 5% - 예외적 역량
        80-89: 상위 20% - 우수한 역량
        70-79: 평균 - 기본 요구사항 충족
        60-69: 기대 이하 - 중요한 격차
        0-59: 부적합 - 근본적 결함
        """
    
    def _default_weights(self) -> Dict[str, float]:
        """기본 가중치"""
        return {
            "job_expertise": 0.30,
            "analytical": 0.15,
            "execution": 0.20,
            "relationship": 0.15,
            "resilience": 0.10,
            "influence": 0.10,
        }

    def _enrich_evidence_with_transcript_info(
        self,
        evidence_list: List[Dict[str, Any]],
        structured_transcript: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        LLM이 생성한 evidence 목록에 structured_transcript 정보를 추가합니다.
        """
        enriched_evidence = []
        transcript_map = {utterance["id"]: utterance for utterance in structured_transcript}

        for evidence_item in evidence_list:
            turn_id = evidence_item.get("turn")
            if turn_id and turn_id in transcript_map:
                utterance = transcript_map[turn_id]
                evidence_item["linked_utterance"] = {
                    "id": utterance.get("id"),
                    "speaker": utterance.get("speaker"),
                    "text": utterance.get("text"),
                    "start_time": utterance.get("start_time"),
                    "end_time": utterance.get("end_time"),
                }
            enriched_evidence.append(evidence_item)
        return enriched_evidence