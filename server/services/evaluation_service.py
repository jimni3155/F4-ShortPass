"""
Evaluation Service
Orchestrates candidate evaluation using multiagent system.
Replaces legacy ScoreAggregator and MatchingScorer with comprehensive LLM-based evaluation.
"""

import json
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

# Import multiagent evaluator
from ai.agents.multiagent_evaluator import MultiAgentEvaluator

# Import models
from models.interview import Applicant
from models.job import Job
from models.interview import InterviewSession as Interview
from models.evaluation import Evaluation


class EvaluationService:
    """
    Service layer for candidate evaluation using multiagent system.
    
    Key Features:
    - Evaluates entire interview context (not just individual answers)
    - Utilizes resume across all competencies
    - Dynamically generates evaluation criteria based on JD
    - Produces comprehensive match analysis
    """
    
    def __init__(self):
        self.evaluator = MultiAgentEvaluator()
    
    async def evaluate_applicant_for_job(
        self,
        db: Session,
        applicant_id: int,
        job_id: int,
        interview_id: Optional[int] = None
    ) -> dict:
        """
        Evaluate applicant for a specific job using multiagent system.
        
        Process:
        1. Fetch interview transcript, resume, and JD
        2. Validate data completeness
        3. Run 6 parallel evaluator agents
        4. Aggregate results
        5. Calculate final match score
        6. Persist evaluation
        
        Args:
            db: Database session
            applicant_id: Applicant to evaluate
            job_id: Job to evaluate against
            interview_id: Specific interview (or most recent if None)
        
        Returns:
            {
                "evaluation_id": int,
                "applicant_id": int,
                "job_id": int,
                "match_score": float (0-100),
                "competency_scores": dict,
                "recommendation": str,
                "timestamp": str
            }
        """
        try:
            # 1. Fetch data
            applicant = self._get_applicant(db, applicant_id)
            job = self._get_job(db, job_id)
            interview = self._get_interview(db, applicant_id, interview_id)
            
            # 2. Validate
            self._validate_data(applicant, job, interview)
            
            # 3. Prepare inputs
            evaluation_input = self._prepare_input(applicant, job, interview)
            
            # 4. Run multiagent evaluation
            result = await self.evaluator.evaluate(
                interview_transcript=evaluation_input["transcript"],
                resume=evaluation_input["resume"],
                job_description=evaluation_input["jd"],
                category_weights=evaluation_input["weights"],
                position_type=evaluation_input["position_type"]
            )
            
            # 5. Save to DB
            evaluation_record = self._save_evaluation(
                db, applicant_id, job_id, interview.id if interview else None, result
            )
            
            # 6. Return summary
            return {
                "evaluation_id": evaluation_record.id,
                "applicant_id": applicant_id,
                "job_id": job_id,
                "match_score": result["match_result"]["match_score"],
                "competency_scores": result["aggregated_evaluation"]["competency_scores"],
                "recommendation": result["match_result"]["recommendation"]["decision"],
                "timestamp": evaluation_record.created_at.isoformat()
            }
        
        except ValueError as e:
            raise ValueError(f"Evaluation failed: {str(e)}")
        except SQLAlchemyError as e:
            db.rollback()
            raise SQLAlchemyError(f"Database error: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")
    
    # Data Fetching
    
    def _get_applicant(self, db: Session, applicant_id: int) -> Applicant:
        """Fetch applicant with resume."""
        applicant = db.query(Applicant).filter(Applicant.id == applicant_id).first()
        if not applicant:
            raise ValueError(f"Applicant {applicant_id} not found")
        return applicant
    
    def _get_job(self, db: Session, job_id: int) -> Job:
        """Fetch job with category_weights (from JD processing)."""
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        if not job.category_weights:
            raise ValueError(
                f"Job {job_id} missing category_weights. "
                "Run JD processing first to extract competency weights."
            )
        
        return job
    
    def _get_interview(
        self,
        db: Session,
        applicant_id: int,
        interview_id: Optional[int]
    ) -> Interview:
        """Fetch interview with transcript."""
        if interview_id:
            interview = db.query(Interview).filter(
                Interview.id == interview_id,
                Interview.applicant_id == applicant_id
            ).first()
            if not interview:
                raise ValueError(f"Interview {interview_id} not found")
        else:
            # Most recent completed interview
            interview = db.query(Interview).filter(
                Interview.applicant_id == applicant_id,
                Interview.status == "completed"
            ).order_by(Interview.created_at.desc()).first()
            
            if not interview:
                raise ValueError(f"No completed interview for applicant {applicant_id}")
        
        return interview
    
    # Data Validation
    
    def _validate_data(
        self,
        applicant: Applicant,
        job: Job,
        interview: Interview
    ) -> None:
        """Validate all required data is present."""
        # Resume
        if not applicant.resume_file_path:
            raise ValueError("Resume missing")
        
        # Interview transcript
        if not interview.transcript:
            raise ValueError("Interview transcript missing")
        
        # JD
        if not job.description:
            raise ValueError("Job description missing")
        
        # Competency weights
        required = [
            "job_expertise",
            "problem_solving",
            "organizational_fit",
            "growth_potential",
            "interpersonal_skill",
            "achievement_motivation"
        ]
        
        for comp in required:
            if comp not in job.category_weights:
                raise ValueError(f"Missing weight for {comp}")
    
    # Input Preparation
    
    def _prepare_input(
        self,
        applicant: Applicant,
        job: Job,
        interview: Interview
    ) -> dict:
        """Prepare clean inputs for multiagent evaluator."""
        return {
            "transcript": interview.transcript,
            "resume": self._get_resume_text(applicant),
            "jd": {
                "title": job.title,
                "description": job.description,
                "requirements": getattr(job, 'requirements', []),
                "company": job.company.name if job.company else "Unknown"
            },
            "weights": job.category_weights,
            "position_type": job.position_type or "기술 중심"
        }
    
    def _get_resume_text(self, applicant: Applicant) -> str:
        """Get resume as text."""
        # Extract from file if needed
        if applicant.resume_file_path:
            return self._extract_from_file(applicant.resume_file_path)
        
        raise ValueError("Resume text unavailable")
    
    def _extract_from_file(self, file_path: str) -> str:
        """Extract text from resume file (PDF, DOCX, etc)."""
        # TODO: Implement based on your file storage
        # Use Textract, PyPDF2, or similar
        return f"[Resume at {file_path}]"
    
    # Persistence
    
    def _save_evaluation(
        self,
        db: Session,
        applicant_id: int,
        job_id: int,
        interview_id: Optional[int],
        result: dict
    ) -> Evaluation:
        """Save evaluation to database."""
        try:
            evaluation = Evaluation(
                applicant_id=applicant_id,
                job_id=job_id,
                interview_id=interview_id,
                
                # Core scores
                match_score=result["match_result"]["match_score"],
                weighted_score=result["aggregated_evaluation"]["weighted_score"],
                confidence_score=result["aggregated_evaluation"]["confidence_score"],
                
                # Detailed results (JSONB)
                competency_scores=result["aggregated_evaluation"]["competency_scores"],
                individual_evaluations=result["individual_evaluations"],
                aggregated_evaluation=result["aggregated_evaluation"],
                match_result=result["match_result"],
                
                # Metadata
                metadata=result["metadata"],
                
                created_at=datetime.utcnow()
            )
            
            db.add(evaluation)
            db.commit()
            db.refresh(evaluation)
            
            return evaluation
        
        except Exception as e:
            db.rollback()
            raise SQLAlchemyError(f"Failed to save: {str(e)}")
    
    # Query Methods
    async def get_evaluation(self, db: Session, evaluation_id: int) -> Optional[dict]:
        """Get evaluation by ID."""
        eval = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
        if not eval:
            return None
        
        return {
            "evaluation_id": eval.id,
            "applicant_id": eval.applicant_id,
            "job_id": eval.job_id,
            "match_score": eval.match_score,
            "competency_scores": eval.competency_scores,
            "recommendation": eval.match_result.get("recommendation", {}).get("decision"),
            "created_at": eval.created_at.isoformat()
        }
    
    async def get_top_applicants_for_job(
        self,
        db: Session,
        job_id: int,
        min_score: float = 70.0,
        limit: int = 20
    ) -> list[dict]:
        """Get top applicants for a job, ranked by match score."""
        evals = db.query(Evaluation).filter(
            Evaluation.job_id == job_id,
            Evaluation.match_score >= min_score
        ).order_by(Evaluation.match_score.desc()).limit(limit).all()
        
        return [
            {
                "applicant_id": e.applicant_id,
                "match_score": e.match_score,
                "competency_scores": e.competency_scores,
                "recommendation": e.match_result.get("recommendation", {}).get("decision")
            }
            for e in evals
        ]
    
    async def compare_applicants(
        self,
        db: Session,
        job_id: int,
        applicant_ids: list[int]
    ) -> dict:
        """Compare applicants side-by-side for a job."""
        evals = db.query(Evaluation).filter(
            Evaluation.job_id == job_id,
            Evaluation.applicant_id.in_(applicant_ids)
        ).all()
        
        if not evals:
            return {"error": "No evaluations found"}
        
        comparison = {"job_id": job_id, "applicants": []}
        
        for e in evals:
            comparison["applicants"].append({
                "applicant_id": e.applicant_id,
                "match_score": e.match_score,
                "competency_scores": e.competency_scores,
                "strengths": e.aggregated_evaluation.get("synthesis", {}).get("top_strengths", []),
                "concerns": e.aggregated_evaluation.get("synthesis", {}).get("key_concerns", []),
                "recommendation": e.match_result.get("recommendation", {}).get("decision")
            })
        
        # Sort by match score
        comparison["applicants"].sort(key=lambda x: x["match_score"], reverse=True)
        
        return comparison