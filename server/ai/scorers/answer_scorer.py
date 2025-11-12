# app/ai/scorers/answer_scorer.py
"""
개별 면접 답변 평가
"""
from typing import Dict, Any, List
from ai.utils.llm_client import LLMClient
from ai.prompts.evaluation_prompts import EvaluationPromptBuilder
from schemas.interview import AnswerEvaluation, Question


class AnswerScorer:
    """개별 답변을 평가하는 클래스"""
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.prompt_builder = EvaluationPromptBuilder()
    
    async def evaluate_answer(
        self,
        question: Question,
        answer_text: str,
        context: Dict[str, Any]
    ) -> AnswerEvaluation:
        """
        단일 답변 평가
        
        Args:
            question: 질문 객체 (평가 차원, 가중치 포함)
            answer_text: 지원자 답변
            context: 추가 컨텍스트 (지원자 프로필 등)
        
        Returns:
            AnswerEvaluation: 평가 결과
        """
        # 1. 프롬프트 생성
        prompt = self.prompt_builder.build_evaluation_prompt(
            question=question,
            answer=answer_text,
            context=context
        )
        
        # 2. LLM 호출 (구조화된 출력)
        response = await self.llm.generate(
            prompt=prompt,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "answer_evaluation",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "scores": {
                                "type": "object",
                                "description": "평가 차원별 점수 (0-100)",
                                "additionalProperties": {"type": "number"}
                            },
                            "reasoning": {
                                "type": "string",
                                "description": "평가 근거"
                            },
                            "matched_keywords": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "답변에서 발견된 주요 키워드"
                            },
                            "missing_keywords": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "언급되지 않은 기대 키워드"
                            },
                            "strengths": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "답변의 강점"
                            },
                            "weaknesses": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "답변의 약점"
                            }
                        },
                        "required": ["scores", "reasoning"]
                    }
                }
            },
            temperature=0.3
        )
        
        # 3. 키워드 매칭 보조 평가
        keyword_match = self._evaluate_keyword_match(
            answer=answer_text,
            expected_keywords=question.expected_keywords or []
        )
        
        # 4. 결과 반환
        return AnswerEvaluation(
            question_id=question.id,
            question_text=question.question_text,
            question_type=question.question_type,
            answer_text=answer_text,
            scores=response["scores"],
            evaluation_detail=response["reasoning"],
            matched_keywords=response.get("matched_keywords", []),
            missing_keywords=response.get("missing_keywords", []),
            strengths=response.get("strengths", []),
            weaknesses=response.get("weaknesses", [])
        )
    
    async def evaluate_multiple_answers(
        self,
        qa_pairs: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> List[AnswerEvaluation]:
        """
        여러 답변을 배치로 평가
        
        Args:
            qa_pairs: [{"question": Question, "answer": str}, ...]
            context: 공통 컨텍스트
        
        Returns:
            List[AnswerEvaluation]: 평가 결과 리스트
        """
        evaluations = []
        
        for qa in qa_pairs:
            evaluation = await self.evaluate_answer(
                question=qa["question"],
                answer_text=qa["answer"],
                context=context
            )
            evaluations.append(evaluation)
        
        return evaluations
    
    def _evaluate_keyword_match(
        self,
        answer: str,
        expected_keywords: List[str]
    ) -> Dict[str, Any]:
        """키워드 매칭 보조 평가"""
        if not expected_keywords:
            return {"matched": [], "missing": [], "score": 100}
        
        answer_lower = answer.lower()
        matched = [kw for kw in expected_keywords if kw.lower() in answer_lower]
        missing = [kw for kw in expected_keywords if kw.lower() not in answer_lower]
        
        score = (len(matched) / len(expected_keywords)) * 100 if expected_keywords else 100
        
        return {
            "matched": matched,
            "missing": missing,
            "score": score
        }