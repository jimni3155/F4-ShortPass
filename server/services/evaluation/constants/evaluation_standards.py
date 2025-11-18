# services/evaluation/constants/evaluation_standards.py
"""
역량별 절대평가 기준표

모든 산업, 직무, 부서에 적용 가능한 보편적 기준을 정의합니다.
각 역량은 5개 등급(90-100, 80-89, 70-79, 60-69, 0-59)으로 평가됩니다.
"""

from typing import Dict, List
from dataclasses import dataclass


@dataclass
class ScoreStandard:
    """점수 기준 구조"""
    overall: str  # 전체 수준 설명
    details: Dict[str, str]  # 세부항목별 기준
    indicators: List[str]  # 관찰 가능한 지표


# ==================== 1. ANALYTICAL (분석적 사고) ====================

ANALYTICAL_STANDARDS = {
    "90-100": ScoreStandard(
        overall="업계 상위 5% 수준. 복잡하고 모호한 문제를 독립적으로 구조화하여 해결할 수 있는 수준",
        details={
            "problem_solving": "다차원적 문제를 체계적으로 분해하고, 근본 원인을 파악하여 창의적 해결책 도출",
            "strategic_thinking": "장기적 관점에서 비즈니스 임팩트를 고려한 전략 수립. 2-3단계 선행 사고 가능",
            "analytical_thinking": "정량/정성 데이터를 종합 분석. 숨겨진 패턴과 인사이트 도출",
            "decision_making": "불확실한 상황에서도 명확한 의사결정 기준 제시. 트레이드오프를 구체적 근거로 설명"
        },
        indicators=[
            "문제를 3개 이상의 관점에서 분석하고 각각의 장단점 제시",
            "데이터 기반으로 의사결정하며, 가정과 제약조건을 명시",
            "예상되는 리스크와 대응 방안을 사전에 고려",
            "복잡한 개념을 단순하고 명확하게 설명",
            "Why를 3번 이상 질문하여 근본 원인 탐색",
            "대안 비교 시 정량적 지표(비용, 시간, 효과 등) 활용"
        ]
    ),
    
    "80-89": ScoreStandard(
        overall="업계 상위 20% 수준. 구조화된 문제를 논리적으로 분석하고 해결할 수 있는 수준",
        details={
            "problem_solving": "명확한 문제는 독립적으로 해결. 복잡한 문제는 가이드 하에 해결 가능",
            "strategic_thinking": "중기적 관점(6개월~1년)에서 계획 수립 가능. 비즈니스 목표와 연결",
            "analytical_thinking": "주요 데이터 포인트를 파악하고 의미있는 분석 수행",
            "decision_making": "주요 선택지의 장단점을 비교하여 합리적 결정. 근거 제시 가능"
        },
        indicators=[
            "문제의 핵심을 정확히 파악하고 구조화",
            "논리적 흐름이 명확하며 비약 없음",
            "주요 가정을 명시하고 검증 방법 제시",
            "과거 경험에서 패턴을 찾아 현재 상황에 적용",
            "의사결정 시 2-3가지 대안 비교",
            "질문에 대한 답변이 구체적이고 근거가 명확"
        ]
    ),
    
    "70-79": ScoreStandard(
        overall="평균 수준. 기본적인 분석과 문제해결이 가능하나 깊이와 독창성이 제한적",
        details={
            "problem_solving": "정형화된 문제는 해결 가능. 비정형 문제는 도움 필요",
            "strategic_thinking": "단기적 계획(1-3개월) 수립 가능. 장기 전략은 부족",
            "analytical_thinking": "기본 데이터 해석 가능. 심층 분석은 어려움",
            "decision_making": "주요 옵션 파악 가능. 복잡한 트레이드오프 판단은 어려움"
        },
        indicators=[
            "문제를 이해하고 있으나 구조화는 미흡",
            "기본적인 논리 전개는 가능하나 비약이 있음",
            "질문에는 답하나 깊이있는 설명 부족",
            "경험을 언급하나 추상적이고 일반적",
            "대안 제시가 1-2개로 제한적",
            "Why 질문에 표면적 답변"
        ]
    ),
    
    "60-69": ScoreStandard(
        overall="기대치 이하. 기본적인 사고 과정은 있으나 논리성과 체계성이 부족",
        details={
            "problem_solving": "문제 파악에 어려움. 해결 방법 제시가 모호",
            "strategic_thinking": "즉각적 대응에 집중. 전략적 사고 부족",
            "analytical_thinking": "데이터 해석 미숙. 주관적 판단에 의존",
            "decision_making": "선택의 근거가 불명확. 일관성 부족"
        },
        indicators=[
            "문제의 핵심을 파악하지 못함",
            "논리적 비약이 많고 인과관계 불명확",
            "질문 의도를 자주 오해",
            "구체적 사례 제시 어려움",
            "답변이 산만하고 요점 없음",
            "Why 질문에 답변 회피 또는 반복"
        ]
    ),
    
    "0-59": ScoreStandard(
        overall="부적합. 분석적 사고 능력이 현저히 부족",
        details={
            "problem_solving": "문제 인식 자체가 어려움",
            "strategic_thinking": "전략적 사고 거의 없음",
            "analytical_thinking": "분석 능력 매우 미흡",
            "decision_making": "의사결정 과정이 불명확하거나 비논리적"
        },
        indicators=[
            "질문과 무관한 답변",
            "논리적 연결고리 없음",
            "경험/사례 제시 불가",
            "일관성 없는 주장",
            "기본 개념 이해 부족"
        ]
    )
}


# ==================== 2. EXECUTION (실행력) ====================

EXECUTION_STANDARDS = {
    "90-100": ScoreStandard(
        overall="업계 상위 5% 수준. 복잡한 프로젝트를 주도적으로 완수하며 탁월한 성과 창출",
        details={
            "execution_ability": "다수의 프로젝트를 동시에 관리하며 모두 성공적으로 완수. 예상 일정보다 빠르거나 예산 내 완료",
            "ownership": "프로젝트의 성공을 자신의 책임으로 인식. 장애물을 주도적으로 제거하고 결과에 대해 책임",
            "performance_accountability": "구체적이고 측정 가능한 성과 지표 달성. 정량적 임팩트 제시 가능",
            "priority_management": "긴급도와 중요도를 명확히 구분. 우선순위를 비즈니스 목표에 정렬"
        },
        indicators=[
            "3개 이상의 프로젝트를 성공적으로 완수한 구체적 사례",
            "성과를 정량적으로 표현 (매출 X% 증가, 비용 Y% 절감, 시간 Z% 단축 등)",
            "예상치 못한 문제 발생 시 대응 방안 수립 및 실행 경험",
            "마감 기한을 지키기 위한 구체적 전략과 실행",
            "리소스 제약 상황에서도 목표 달성",
            "프로젝트 실패 경험과 교훈, 개선 사항 명확히 설명"
        ]
    ),
    
    "80-89": ScoreStandard(
        overall="업계 상위 20% 수준. 프로젝트를 안정적으로 완수하며 기대 이상의 성과 달성",
        details={
            "execution_ability": "대부분의 프로젝트를 일정 내 완료. 품질 기준 충족",
            "ownership": "맡은 업무에 책임감 있게 접근. 문제 발생 시 적극적으로 해결 시도",
            "performance_accountability": "목표 대비 성과 추적. 주요 KPI 달성",
            "priority_management": "업무의 우선순위를 파악하고 중요한 것부터 처리"
        },
        indicators=[
            "1-2개의 의미있는 프로젝트 완수 사례",
            "성과를 설명할 때 Before/After 비교 가능",
            "일정 지연 시 조기 공유 및 대응",
            "업무 진행 상황을 주기적으로 체크하고 보고",
            "목표 달성을 위한 구체적 액션 플랜 수립",
            "작은 실수에서 빠르게 학습하고 개선"
        ]
    ),
    
    "70-79": ScoreStandard(
        overall="평균 수준. 주어진 업무를 수행하나 주도성과 완성도가 다소 부족",
        details={
            "execution_ability": "명확한 업무는 수행 가능. 모호한 상황에서 어려움",
            "ownership": "지시된 업무는 수행하나 주도적 문제 해결은 제한적",
            "performance_accountability": "기본적인 성과는 내나 측정 가능한 임팩트는 부족",
            "priority_management": "우선순위 파악하나 실행에서 혼선"
        },
        indicators=[
            "프로젝트 경험은 있으나 주도적 역할은 아님",
            "성과를 정성적으로만 설명 (정량 지표 없음)",
            "마감 준수하나 일정 관리는 타인 의존",
            "문제 발생 시 보고는 하나 해결 시도는 제한적",
            "계획 수립은 하나 실행 모니터링 부족",
            "완성도보다 완료에 집중"
        ]
    ),
    
    "60-69": ScoreStandard(
        overall="기대치 이하. 업무 완수 능력이 부족하고 책임감이 약함",
        details={
            "execution_ability": "단순 업무만 수행 가능. 프로젝트 완수 경험 제한적",
            "ownership": "수동적 태도. 문제를 타인에게 전가",
            "performance_accountability": "성과 측정 부재. 결과보다 과정에 집중",
            "priority_management": "우선순위 판단 미흡. 중요하지 않은 일에 시간 소비"
        },
        indicators=[
            "의미있는 프로젝트 완수 사례 부족",
            "성과를 막연하게 표현 ('열심히 했다' 등)",
            "일정 지연이 빈번하거나 예측 불가",
            "문제 발생 시 회피하거나 변명",
            "계획 없이 즉흥적으로 일 처리",
            "완료되지 않은 일이 많음"
        ]
    ),
    
    "0-59": ScoreStandard(
        overall="부적합. 실행 능력이 현저히 부족",
        details={
            "execution_ability": "기본 업무도 완수 어려움",
            "ownership": "책임 회피. 타인 탓",
            "performance_accountability": "성과 개념 부재",
            "priority_management": "업무 관리 능력 없음"
        },
        indicators=[
            "구체적 성과 사례 없음",
            "책임감 없는 태도",
            "기본 업무도 미완료",
            "시간 관리 능력 없음"
        ]
    )
}


# ==================== 3. RELATIONSHIP (관계 형성) ====================

RELATIONSHIP_STANDARDS = {
    "90-100": ScoreStandard(
        overall="업계 상위 5% 수준. 다양한 이해관계자와 탁월한 관계를 구축하고 협업을 주도",
        details={
            "communication": "복잡한 내용을 대상에 맞춰 명확히 전달. 경청하고 핵심을 파악",
            "collaboration": "팀 성과를 위해 적극 기여. 다른 팀/부서와 원활히 협업하여 시너지 창출",
            "conflict_management": "갈등을 건설적으로 해결. Win-Win 솔루션 도출",
            "organizational_adaptability": "다양한 조직 문화와 일하는 방식에 빠르게 적응하고 융화"
        },
        indicators=[
            "크로스펑셔널 협업으로 의미있는 성과를 낸 구체적 사례",
            "의견 충돌 상황에서 합의점을 도출한 경험",
            "어려운 이해관계자를 설득한 사례",
            "다양한 배경의 사람들과 협업 경험 (타부서, 외부 파트너 등)",
            "커뮤니케이션 스타일을 상대방에 맞춰 조정",
            "팀 내 갈등 조정자 역할 경험",
            "피드백을 건설적으로 주고받음"
        ]
    ),
    
    "80-89": ScoreStandard(
        overall="업계 상위 20% 수준. 대부분의 상황에서 원활한 소통과 협업 가능",
        details={
            "communication": "명확하고 효과적인 의사소통. 필요 시 적절히 조율",
            "collaboration": "팀워크를 중시하고 협업에 적극적. 역할 분담 잘함",
            "conflict_management": "갈등을 인식하고 해결 노력. 대부분 원만히 해결",
            "organizational_adaptability": "새로운 환경에 적응. 조직 규범 이해하고 따름"
        },
        indicators=[
            "팀 프로젝트에서 적극적 역할 수행",
            "의견 차이 발생 시 열린 대화로 해결",
            "다양한 직무의 동료들과 협업 경험",
            "요청사항을 명확히 전달하고 확인",
            "타인의 의견을 경청하고 존중",
            "업무 관련 커뮤니케이션이 원활"
        ]
    ),
    
    "70-79": ScoreStandard(
        overall="평균 수준. 기본적 소통과 협업은 가능하나 복잡한 상황에서 한계",
        details={
            "communication": "일상적 의사소통은 가능. 복잡한 내용 전달은 어려움",
            "collaboration": "지시된 협업은 수행. 주도적 협력은 제한적",
            "conflict_management": "갈등 회피 경향. 해결보다는 참거나 타협",
            "organizational_adaptability": "적응에 시간 소요. 익숙한 환경 선호"
        },
        indicators=[
            "팀 프로젝트 경험은 있으나 보조 역할",
            "의견 충돌 시 수동적",
            "친한 동료와만 편하게 소통",
            "커뮤니케이션 오해가 가끔 발생",
            "피드백에 방어적",
            "새로운 사람/환경에 경계"
        ]
    ),
    
    "60-69": ScoreStandard(
        overall="기대치 이하. 소통과 협업에 어려움이 있고 관계 형성 미흡",
        details={
            "communication": "의사소통 명확성 부족. 오해 빈번",
            "collaboration": "협업 기피 또는 비효율적",
            "conflict_management": "갈등 해결 능력 없음. 악화시키거나 회피",
            "organizational_adaptability": "적응 어려움. 불평 많음"
        },
        indicators=[
            "혼자 일하는 것 선호",
            "의견 충돌 시 감정적 대응",
            "소통 오해로 인한 문제 빈번",
            "피드백 거부 또는 무시",
            "팀워크 경험 거의 없음",
            "새 환경 적응 실패 경험"
        ]
    ),
    
    "0-59": ScoreStandard(
        overall="부적합. 대인관계 및 협업 능력 현저히 부족",
        details={
            "communication": "의사소통 매우 미흡",
            "collaboration": "협업 불가",
            "conflict_management": "갈등 유발 또는 방치",
            "organizational_adaptability": "조직 적응 불가"
        },
        indicators=[
            "기본적 소통 불가",
            "팀워크 경험 전무",
            "대인 갈등 빈번",
            "피드백 수용 불가"
        ]
    )
}


# ==================== 4. RESILIENCE (회복탄력성) ====================

RESILIENCE_STANDARDS = {
    "90-100": ScoreStandard(
        overall="업계 상위 5% 수준. 극심한 압박과 실패 상황에서도 빠르게 회복하고 성장",
        details={
            "learning_agility": "새로운 기술/지식을 빠르게 습득하고 적용. 변화를 기회로 활용",
            "resilience": "좌절과 실패를 성장의 기회로 삼음. 압박 상황에서도 안정적 퍼포먼스",
            "stress_management": "고강도 스트레스 상황에서도 침착함 유지. 건강한 대응 방식 보유",
            "self_development": "지속적 자기개발에 투자. 피드백을 적극 수용하고 개선"
        },
        indicators=[
            "큰 실패나 좌절 후 빠르게(1-3개월) 회복하여 더 나은 성과 달성",
            "압박 상황에서 오히려 집중력과 생산성 향상",
            "새로운 기술/분야를 3개월 이내 습득하여 실무 적용",
            "부정적 피드백을 구체적 개선 계획으로 전환",
            "위기 상황에서 팀을 이끈 경험",
            "변화를 긍정적으로 받아들이고 적극 대응",
            "스트레스 관리를 위한 체계적 방법론 보유"
        ]
    ),
    
    "80-89": ScoreStandard(
        overall="업계 상위 20% 수준. 어려운 상황을 잘 극복하고 지속적으로 성장",
        details={
            "learning_agility": "새로운 것을 학습하는 속도가 빠름. 적응력 좋음",
            "resilience": "실패에서 교훈을 얻고 개선. 대부분 잘 회복",
            "stress_management": "스트레스를 효과적으로 관리. 안정적 퍼포먼스 유지",
            "self_development": "자기계발에 투자. 피드백 수용적"
        },
        indicators=[
            "실패 경험을 솔직히 공유하고 배운 점 설명",
            "어려운 상황에서도 포기하지 않고 해결 노력",
            "6개월 이내 새로운 기술 습득",
            "스트레스 상황에서도 품질 유지",
            "피드백을 받아들이고 개선 시도",
            "지속적으로 학습하는 습관"
        ]
    ),
    
    "70-79": ScoreStandard(
        overall="평균 수준. 일반적인 어려움은 극복하나 큰 압박에는 취약",
        details={
            "learning_agility": "학습 가능하나 시간 소요. 변화에 다소 불편",
            "resilience": "작은 실패는 극복. 큰 좌절에는 회복 오래 걸림",
            "stress_management": "일상적 스트레스는 관리. 고강도는 어려움",
            "self_development": "필요할 때만 학습. 자발적 개발은 제한적"
        },
        indicators=[
            "실패 언급은 하나 교훈 도출은 피상적",
            "압박 시 퍼포먼스 저하",
            "새로운 기술 학습에 소극적",
            "피드백에 수용적이나 실천은 느림",
            "변화에 적응하는데 시간 필요",
            "스트레스 관리 방법 모호"
        ]
    ),
    
    "60-69": ScoreStandard(
        overall="기대치 이하. 압박에 약하고 회복력 부족. 성장 의지 미흡",
        details={
            "learning_agility": "학습 속도 느림. 변화 거부",
            "resilience": "실패에서 회복 어려움. 좌절 시 오래 침체",
            "stress_management": "스트레스에 취약. 퍼포먼스 급격히 저하",
            "self_development": "자기개발 동기 부족. 현 상태 안주"
        },
        indicators=[
            "실패를 인정하지 않거나 타인 탓",
            "압박 시 회피하거나 번아웃",
            "새로운 것 학습 거부",
            "피드백에 방어적이고 개선 없음",
            "변화를 두려워하고 저항",
            "스트레스 대처 미숙"
        ]
    ),
    
    "0-59": ScoreStandard(
        overall="부적합. 회복탄력성과 학습 능력 현저히 부족",
        details={
            "learning_agility": "학습 의지/능력 없음",
            "resilience": "실패 시 포기",
            "stress_management": "스트레스 대응 불가",
            "self_development": "성장 의지 없음"
        },
        indicators=[
            "실패 경험 회피",
            "압박 시 기능 정지",
            "학습 거부",
            "피드백 무시",
            "현재 상태 고수"
        ]
    )
}


# ==================== 5. INFLUENCE (영향력) ====================

INFLUENCE_STANDARDS = {
    "90-100": ScoreStandard(
        overall="업계 상위 5% 수준. 조직에 강력한 긍정적 영향을 미치고 변화를 주도",
        details={
            "vision_setting": "명확하고 설득력있는 비전 제시. 구성원들을 동기부여하고 방향 정렬",
            "coaching_development": "타인의 성장을 적극 지원. 효과적인 코칭과 멘토링으로 팀 역량 향상",
            "change_management": "변화를 주도하고 저항 관리. 조직 전반의 혁신 이끔",
            "culture_building": "긍정적 조직 문화 조성. 가치와 규범을 체화하고 전파"
        },
        indicators=[
            "3명 이상의 후배/동료 성장에 직접 기여한 사례",
            "부정적 상황을 긍정적으로 전환한 경험",
            "조직 차원의 변화를 주도하고 실행",
            "어려운 의사결정을 내리고 구성원 설득",
            "팀의 비전과 목표를 명확히 제시하고 공유",
            "갈등을 중재하고 팀 분위기 개선",
            "롤모델로 인정받는 경험",
            "조직 내 네트워크를 활용해 시너지 창출"
        ]
    ),
    
    "80-89": ScoreStandard(
        overall="업계 상위 20% 수준. 팀에 긍정적 영향을 주고 리더십 발휘",
        details={
            "vision_setting": "팀 목표를 명확히 전달. 구성원 동기부여",
            "coaching_development": "후배/동료를 지원하고 조언. 실질적 도움 제공",
            "change_management": "변화를 수용하고 팀 적응 도움",
            "culture_building": "긍정적 태도로 팀 분위기에 기여"
        },
        indicators=[
            "1-2명의 후배 멘토링 경험",
            "프로젝트에서 팀원들의 참여 이끌어냄",
            "어려운 상황에서 팀 사기 진작",
            "새로운 방식/프로세스 제안하고 실행",
            "팀 목표 달성을 위해 주도적 역할",
            "갈등 상황에서 중재 시도"
        ]
    ),
    
    "70-79": ScoreStandard(
        overall="평균 수준. 기본적인 영향력은 있으나 리더십은 제한적",
        details={
            "vision_setting": "방향성 이해하고 따름. 제시는 어려움",
            "coaching_development": "요청 시 도움 제공. 주도적 지원은 제한적",
            "change_management": "변화를 수용하나 주도하지 않음",
            "culture_building": "팀 문화에 적응. 형성에는 기여 적음"
        },
        indicators=[
            "멘토링 경험 제한적",
            "팀 활동에 참여하나 주도 안 함",
            "변화에 따라가는 수준",
            "개인 업무에 집중",
            "리더십 발휘 기회 적음",
            "영향력 범위가 좁음"
        ]
    ),
    
    "60-69": ScoreStandard(
        overall="기대치 이하. 영향력 거의 없고 리더십 부재",
        details={
            "vision_setting": "방향성 이해 부족",
            "coaching_development": "타인 성장에 무관심",
            "change_management": "변화 저항 또는 무관심",
            "culture_building": "조직 문화 이해 부족"
        },
        indicators=[
            "멘토링/코칭 경험 없음",
            "팀 활동에 소극적",
            "변화를 따르지 않음",
            "개인주의적",
            "리더십 의지 없음",
            "영향력 없음"
        ]
    ),
    
    "0-59": ScoreStandard(
        overall="부적합. 영향력과 리더십 능력 현저히 부족",
        details={
            "vision_setting": "방향 제시 불가",
            "coaching_development": "타인 개발 능력 없음",
            "change_management": "변화 주도 불가",
            "culture_building": "문화 형성 기여 없음"
        },
        indicators=[
            "리더십 경험 전무",
            "타인에게 부정적 영향",
            "팀워크 방해",
            "변화 저항"
        ]
    )
}


# ==================== 6. JOB EXPERTISE (직무 전문성) ====================

JOB_EXPERTISE_STANDARDS = {
    "90-100": ScoreStandard(
        overall="업계 상위 5% 수준. 해당 직무의 전문가로서 즉시 고도의 업무 수행 가능",
        details={
            "technical_skills": "요구되는 모든 기술을 깊이있게 보유. 최신 트렌드까지 파악",
            "domain_knowledge": "도메인에 대한 깊은 이해. 복잡한 문제를 독립적으로 해결",
            "practical_experience": "다양하고 복잡한 실무 경험. 큰 임팩트를 만든 프로젝트 다수",
            "problem_solving_in_domain": "직무 특화된 문제해결 능력 탁월. 창의적 솔루션 도출"
        },
        indicators=[
            "요구 기술 스택을 실전 프로젝트에서 3년 이상 활용",
            "복잡한 기술 문제를 독립적으로 해결한 사례",
            "정량적 성과 (성능 X% 개선, 비용 Y% 절감 등)",
            "기술적 의사결정을 주도하고 아키텍처 설계 경험",
            "최신 기술 트렌드를 파악하고 적용 시도",
            "기술 블로그, 오픈소스 기여, 컨퍼런스 발표 등",
            "기술 이슈에 대한 깊이있는 설명과 트레이드오프 논의",
            "Junior 개발자 멘토링 및 기술 리뷰 경험"
        ]
    ),
    
    "80-89": ScoreStandard(
        overall="업계 상위 20% 수준. 단기 적응 후 독립적 업무 수행 가능한 전문성 보유",
        details={
            "technical_skills": "핵심 기술을 실무에 활용 가능. 심화 학습 필요",
            "domain_knowledge": "도메인 기본 이해 탄탄. 일반적 문제는 독립 해결",
            "practical_experience": "의미있는 프로젝트 경험. 기여도 명확",
            "problem_solving_in_domain": "일반적 기술 문제는 해결 가능. 복잡한 문제는 가이드 필요"
        },
        indicators=[
            "요구 기술 스택 1-2년 이상 실무 경험",
            "주요 기술 개념을 명확히 이해하고 설명 가능",
            "프로젝트에서 핵심 기능 구현 경험",
            "코드 리뷰 가능하고 품질 이슈 파악",
            "기술 문서 작성 및 공유 경험",
            "트러블슈팅 경험과 해결 과정 설명 가능",
            "기술 스택의 장단점 이해"
        ]
    ),
    
    "70-79": ScoreStandard(
        overall="평균 수준. 기본적인 전문성은 있으나 독립적 업무는 어려움",
        details={
            "technical_skills": "기본 기술 사용 가능. 심화 기능은 미숙",
            "domain_knowledge": "표면적 이해. 깊이 부족",
            "practical_experience": "제한적 프로젝트 경험. 보조 역할 위주",
            "problem_solving_in_domain": "간단한 문제만 해결 가능. 대부분 도움 필요"
        },
        indicators=[
            "요구 기술 스택 6개월-1년 경험",
            "기본 개념은 알지만 실전 적용 미흡",
            "프로젝트 경험은 있으나 역할 불명확",
            "기술 설명이 교과서적",
            "문제 해결 시 검색에 의존",
            "실무 경험보다 학습 경험 위주"
        ]
    ),
    
    "60-69": ScoreStandard(
        overall="기대치 이하. 전문성이 부족하고 상당한 교육 필요",
        details={
            "technical_skills": "기술 이해도 낮음. 기본 사용도 미숙",
            "domain_knowledge": "도메인 이해 부족",
            "practical_experience": "실무 경험 거의 없음",
            "problem_solving_in_domain": "문제 해결 능력 미흡"
        },
        indicators=[
            "요구 기술 경험 6개월 미만",
            "기본 개념도 불확실",
            "프로젝트 경험 없거나 매우 제한적",
            "기술 용어 이해 부족",
            "질문에 구체적 답변 못함",
            "이론만 알고 실전 경험 전무"
        ]
    ),
    
    "0-59": ScoreStandard(
        overall="부적합. 해당 직무에 필요한 전문성 현저히 부족",
        details={
            "technical_skills": "기술 능력 없음",
            "domain_knowledge": "도메인 지식 없음",
            "practical_experience": "관련 경험 전무",
            "problem_solving_in_domain": "문제 해결 불가"
        },
        indicators=[
            "관련 기술 경험 없음",
            "기본 개념 이해 부족",
            "프로젝트 경험 없음",
            "질문 이해 못함"
        ]
    )
}


# ==================== 통합 ====================

ALL_STANDARDS = {
    "analytical": ANALYTICAL_STANDARDS,
    "execution": EXECUTION_STANDARDS,
    "relationship": RELATIONSHIP_STANDARDS,
    "resilience": RESILIENCE_STANDARDS,
    "influence": INFLUENCE_STANDARDS,
    "job_expertise": JOB_EXPERTISE_STANDARDS
}


def get_standard(competency: str, score: int) -> ScoreStandard:
    """
    특정 역량과 점수에 해당하는 기준 반환
    
    Args:
        competency: 역량 이름 (analytical, execution, etc.)
        score: 점수 (0-100)
    
    Returns:
        ScoreStandard 객체
    
    Example:
        >>> std = get_standard("analytical", 85)
        >>> print(std.overall)
        "업계 상위 20% 수준. 구조화된 문제를 논리적으로 분석하고 해결할 수 있는 수준"
    """
    if competency not in ALL_STANDARDS:
        raise ValueError(f"Unknown competency: {competency}")
    
    if score >= 90:
        range_key = "90-100"
    elif score >= 80:
        range_key = "80-89"
    elif score >= 70:
        range_key = "70-79"
    elif score >= 60:
        range_key = "60-69"
    else:
        range_key = "0-59"
    
    return ALL_STANDARDS[competency][range_key]


def get_all_standards_for_competency(competency: str) -> Dict[str, ScoreStandard]:
    """특정 역량의 모든 점수 기준 반환"""
    if competency not in ALL_STANDARDS:
        raise ValueError(f"Unknown competency: {competency}")
    return ALL_STANDARDS[competency]