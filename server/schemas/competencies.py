"""
매칭 시스템 역량 정의
"""

from typing import Dict, Optional
from pydantic import BaseModel

class CompetencyDefinition(BaseModel):
    """역량 정의 스키마"""
    name: str
    name_en: str
    type: str  # "fixed" or "dynamic"
    description: str
    dimensions: Optional[Dict[str, str]] = None
    evaluation_focus: Optional[str] = None

COMPETENCIES: Dict[str, CompetencyDefinition] = {
    "job_expertise": CompetencyDefinition(
        name="직무 전문성",
        name_en="Job Expertise",
        type="dynamic",
        description="직무 수행에 직접 필요한 하드스킬",
        evaluation_focus="기술 스택, 도구, 경험 보유 여부"
    ),
    
    "problem_solving": CompetencyDefinition(
        name="문제해결력",
        name_en="Problem Solving",
        type="fixed",
        description="복잡한 문제의 원인 분석 및 해결 능력",
        dimensions={
            "analytical_thinking": "분석적 사고",
            "creative_solution": "창의적 해결",
            "decision_making": "의사결정",
            "execution": "실행력"
        }
    ),
    
    "organizational_fit": CompetencyDefinition(
        name="조직 적합성",
        name_en="Organizational Fit",
        type="fixed",
        description="회사 가치관 및 문화 일치도",
        dimensions={
            "value_alignment": "가치관 일치",
            "feedback_receptivity": "피드백 수용성",
            "culture_adaptation": "조직 융화력"
        }
    ),
    
    "growth_potential": CompetencyDefinition(
        name="성장 잠재력",
        name_en="Growth Potential",
        type="fixed",
        description="학습과 성장 가능성",
        dimensions={
            "learning_agility": "학습 민첩성",
            "resilience": "회복 탄력성",
            "metacognition": "메타인지"
        }
    ),
    
    "interpersonal_skill": CompetencyDefinition(
        name="대인관계 역량",
        name_en="Interpersonal Skill",
        type="fixed",
        description="타인과의 효과적인 소통 및 협업",
        dimensions={
            "communication": "커뮤니케이션",
            "listening": "경청",
            "collaboration": "협업",
            "conflict_resolution": "갈등 해결"
        }
    ),
    
    "achievement_motivation": CompetencyDefinition(
        name="성취/동기 역량",
        name_en="Achievement/Motivation",
        type="fixed",
        description="목표 달성을 위한 주도성과 열정",
        dimensions={
            "ownership": "주도성",
            "achievement_orientation": "성취 지향",
            "responsibility": "책임감",
            "commitment": "업무 몰입"
        }
    )
}

# Helper 함수

def get_competency(key: str) -> CompetencyDefinition:
    """특정 역량 정의 반환"""
    return COMPETENCIES.get(key)

def get_fixed_competencies() -> Dict[str, CompetencyDefinition]:
    """고정 역량만 반환 (2-6번)"""
    return {k: v for k, v in COMPETENCIES.items() if v.type == "fixed"}

def get_dynamic_competencies() -> Dict[str, CompetencyDefinition]:
    """동적 역량만 반환 (1번)"""
    return {k: v for k, v in COMPETENCIES.items() if v.type == "dynamic"}