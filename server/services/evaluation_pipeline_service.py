# server/services/evaluation_pipeline_service.py
"""
면접 평가 파이프라인을 실행하고 중간 산출물을 S3(시뮬레이션)에 저장하는 서비스
"""
import json
from .local_s3_service import LocalS3Service

class EvaluationPipelineService:
    def __init__(self, s3_service: LocalS3Service):
        self.s3 = s3_service

    def run_pipeline(self, company_id: int, job_id: int, applicant_id: int, interview_id: int) -> dict:
        """
        전체 평가 파이프라인을 실행하고 로그를 저장합니다.
        현재는 모든 단계에서 모의(mock) 데이터를 생성하고 저장합니다.
        """
        print(f"\n Starting evaluation pipeline for interview {interview_id}...")

        # 1. 기본 경로 설정
        pipeline_version = "v1-pipeline"
        base_key = f"company/{company_id}/job/{job_id}/applicant/{applicant_id}/interview/{interview_id}/{pipeline_version}"

        # 2. 각 단계별 모의 데이터 생성 및 S3(로컬) 저장
        # 01_transcript.json
        transcript_data = self._generate_mock_transcript()
        self.s3.save_json_log(transcript_data, f"{base_key}/01_transcript.json")

        # 10_persona_job_expertise.json
        job_expertise_data = self._generate_mock_persona_eval("job_expertise")
        self.s3.save_json_log(job_expertise_data, f"{base_key}/10_persona_job_expertise.json")

        # 11_persona_soft_skills.json (가정)
        soft_skills_data = self._generate_mock_persona_eval("soft_skills")
        self.s3.save_json_log(soft_skills_data, f"{base_key}/11_persona_soft_skills.json")

        # 20_aggregation_input.json
        agg_input_data = {
            "job_expertise": job_expertise_data["parsed_output"],
            "soft_skills": soft_skills_data["parsed_output"],
            "competency_weights": {"job_expertise": 0.6, "soft_skills": 0.4}
        }
        self.s3.save_json_log(agg_input_data, f"{base_key}/20_aggregation_input.json")
        
        # 21_aggregation_result.json (Python 코드로 실제 계산)
        agg_result_data = self._run_aggregation(agg_input_data)
        self.s3.save_json_log(agg_result_data, f"{base_key}/21_aggregation_result.json")

        # 30_validation_report.json
        validation_data = self._run_validation(agg_result_data)
        self.s3.save_json_log(validation_data, f"{base_key}/30_validation_report.json")
        
        # 40_hr_report_llm_output.json
        hr_report_data = self._generate_hr_report(agg_result_data)
        self.s3.save_json_log(hr_report_data, f"{base_key}/40_hr_report_llm_output.json")

        print(f"✅ Pipeline completed successfully for interview {interview_id}.")
        
        return {
            "message": "Evaluation pipeline completed successfully.",
            "log_path": self.s3.get_log_path(base_key)
        }

    def _generate_mock_transcript(self) -> dict:
        return {
            "interview_id": "interview_1234",
            "dialogue": [
                {"speaker": "interviewer", "text": "자기소개 부탁드립니다."}, 
                {"speaker": "applicant", "text": "네, 안녕하세요. 저는 OOO입니다."}, 
                {"speaker": "interviewer", "text": "가장 자신있는 프로젝트는 무엇인가요?"},
                {"speaker": "applicant", "text": "네, 그것은 OOO 프로젝트입니다..."}
            ]
        }

    def _generate_mock_persona_eval(self, persona_name: str) -> dict:
        """각 페르소나 에이전트의 원본 LLM 응답과 파싱된 결과를 시뮬레이션"""
        return {
            "raw_llm_output": f'{{"score": 85.0, "reasoning": "{persona_name} 측면에서 매우 우수합니다.", "strengths": ["논리적 사고"], "weaknesses": ["경험 부족"]}}',
            "parsed_output": {
                "score": 85.0,
                "reasoning": f"{persona_name} 측면에서 매우 우수합니다.",
                "strengths": ["논리적 사고"],
                "weaknesses": ["경험 부족"]
            },
            "metadata": {
                "model_name": "claude-3-opus-20240229",
                "prompt_version": "v1.2",
                "persona": persona_name
            }
        }
    
    def _run_aggregation(self, agg_input: dict) -> dict:
        """Python 코드로 점수를 계산하는 단계"""
        job_score = agg_input["job_expertise"]["score"]
        soft_score = agg_input["soft_skills"]["score"]
        weights = agg_input["competency_weights"]

        weighted_score = (job_score * weights["job_expertise"]) + (soft_score * weights["soft_skills"])
        
        return {
            "normalized_score": (job_score + soft_score) / 2,
            "weighted_score": weighted_score,
            "match_score": weighted_score, # 예시로 동일하게 설정
            "metadata": {
                "pipeline_version": "aggregation-v1.0",
                "weight_profile": "default_v2"
            }
        }

    def _run_validation(self, agg_result: dict) -> dict:
        """일관성을 검증하는 단계"""
        if agg_result["match_score"] < 60:
            return {"status": "WARN", "issues": ["low_match_score"]}
        return {"status": "OK", "issues": []}

    def _generate_hr_report(self, agg_result: dict) -> dict:
        """최종 HR 리포트 내용을 시뮬레이션"""
        score = agg_result['weighted_score']
        recommendation = "추천" if score > 80 else "보류"
        
        return {
            "recommendation": recommendation,
            "summary": f"종합 점수 {score:.1f}점으로, {recommendation} 대상입니다. 직무 전문성과 소프트 스킬의 가중치를 고려한 결과입니다."
        }
