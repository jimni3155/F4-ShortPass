# server/ai/prompts/parsing_prompts.py
"""
파싱 관련 프롬프트 (JD, 이력서, 포트폴리오)
"""


class ParsingPromptBuilder:
    """파싱 관련 프롬프트"""
    
    def build_jd_parsing_prompt(self, jd_text: str) -> str:
        """JD 파싱 프롬프트"""
        prompt = f"""다음 채용공고를 분석하여 구조화된 정보를 추출해주세요.

=== 채용공고 ===
{jd_text}

=== 추출 항목 ===
1. 필수 기술: "필수", "반드시" 등으로 명시된 기술
2. 우대 기술: "우대", "선호" 등으로 명시된 기술
3. 최소 경력: 명시된 최소 경력 연수 (없으면 0)
4. 선호 도메인: fintech, ecommerce, healthcare 등
5. 특수 경험: startup, leadership, high_traffic 등

=== 출력 형식 ===
{{
  "required_skills": ["Python", "FastAPI", "PostgreSQL"],
  "preferred_skills": ["AWS", "Docker", "Redis"],
  "min_years_experience": 3,
  "preferred_domains": ["fintech"],
  "preferred_special_experience": ["startup_experience"],
  "focus_areas": ["backend", "system_design"]
}}
"""
        return prompt
    
    def build_resume_parsing_prompt(self, resume_text: str) -> str:
        """이력서 파싱 프롬프트"""
        prompt = f"""다음 이력서를 분석하여 주요 정보를 추출해주세요.

=== 이력서 ===
{resume_text}

=== 추출 항목 ===
1. 보유 기술: 명시된 모든 기술 스택
2. 총 경력: 개발 경력 연수
3. 도메인 경험: 어떤 산업/도메인에서 일했는지
4. 특수 경험: 스타트업, 리더십, 대규모 트래픽 등

=== 출력 형식 ===
{{
  "skills": ["Python", "FastAPI", "AWS", "Docker"],
  "total_experience_years": 4,
  "domain_experience": ["fintech", "ecommerce"],
  "special_experience": ["startup_experience", "team_leadership"],
  "education": "서울대학교 컴퓨터공학과",
  "projects": [
    {{
      "name": "프로젝트명",
      "description": "간단한 설명",
      "tech_stack": ["Python", "FastAPI"]
    }}
  ]
}}
"""
        return prompt
    
    def build_portfolio_parsing_prompt(self, portfolio_text: str) -> str:
        """포트폴리오 파싱 프롬프트"""
        prompt = f"""다음 포트폴리오를 분석하여 기술 역량과 경험을 추출해주세요.

=== 포트폴리오 ===
{portfolio_text}

=== 추출 항목 ===
1. 사용 기술: 프로젝트에서 사용한 기술들
2. 프로젝트 복잡도: 프로젝트의 규모와 난이도
3. 주요 성과: 구체적인 성과나 결과
4. 문제 해결 사례: 어떤 문제를 어떻게 해결했는지

=== 출력 형식 ===
{{
  "technical_skills": ["Python", "React", "AWS"],
  "project_complexity": "high",
  "key_achievements": [
    "API 응답 속도 50% 개선",
    "월간 활성 사용자 10만명 달성"
  ],
  "problem_solving_cases": [
    {{
      "problem": "대용량 데이터 처리 성능 이슈",
      "solution": "비동기 처리 및 캐싱 도입",
      "result": "처리 시간 70% 단축"
    }}
  ]
}}
"""
        return prompt
    
    def build_company_values_extraction_prompt(
        self,
        company_values_text: str
    ) -> str:
        """회사 인재상/핵심가치 추출 프롬프트"""
        prompt = f"""다음 회사 인재상을 분석하여 핵심 가치를 추출해주세요.

=== 인재상/핵심 가치 ===
{company_values_text}

=== 추출 항목 ===
회사가 중요하게 생각하는 가치관, 태도, 행동 방식을 추출하세요.

예시 키워드:
- collaboration (협업)
- growth_mindset (성장 마인드셋)
- ownership (주인의식)
- innovation (혁신)
- user_focus (사용자 중심)
- transparency (투명성)
- speed (빠른 실행)

=== 출력 형식 ===
{{
  "core_values": ["collaboration", "growth_mindset", "ownership", "user_focus"],
  "value_descriptions": {{
    "collaboration": "팀워크를 중시하며 함께 성장",
    "growth_mindset": "실패를 두려워하지 않고 끊임없이 학습",
    "ownership": "맡은 일에 책임감을 가지고 주도적으로 실행",
    "user_focus": "항상 사용자 관점에서 생각하고 행동"
  }}
}}
"""
        return prompt

            def build_jd_weight_extraction_prompt(self, jd_text: str) -> str:
        """JD에서 평가 가중치 추출 프롬프트"""
        prompt = f"""다음 채용공고를 분석하여 6가지 평가 역량의 중요도를 파악하고 가중치를 산출해주세요.

=== 채용공고 ===
{jd_text}

=== 6가지 평가 역량 ===
1. job_expertise (직무 전문성)
   - 기술 스택, 도구, 경험 보유 여부
   - 예: "Python 필수", "AWS 경험 3년 이상", "시스템 설계 역량"

2. problem_solving (문제해결력)
   - 분석적 사고, 창의적 해결, 의사결정, 실행력
   - 예: "복잡한 문제 해결", "데이터 기반 의사결정", "알고리즘 최적화"

3. organizational_fit (조직 적합성)
   - 회사 가치관, 문화 일치도
   - 예: "스타트업 문화 적응", "수평적 소통", "애자일 방식"

4. growth_potential (성장 잠재력)
   - 학습 민첩성, 회복 탄력성
   - 예: "빠른 학습 능력", "새로운 기술 습득", "성장 마인드셋"

5. interpersonal_skill (대인관계 역량)
   - 커뮤니케이션, 협업, 갈등 해결
   - 예: "팀워크", "cross-functional 협업", "이해관계자 조율"

6. achievement_motivation (성취/동기 역량)
   - 주도성, 성취 지향, 책임감
   - 예: "주인의식", "목표 지향적", "자발적 업무 수행"

=== 가중치 산출 규칙 ===
- 각 역량의 가중치는 0.0 ~ 1.0 사이
- 6가지 가중치의 합은 반드시 1.0이어야 함
- JD에서 강조하는 키워드가 많을수록 해당 역량 가중치 증가
- 명시적으로 "필수", "중요", "핵심" 등으로 강조된 항목은 가중치 높게

=== 분석 가이드 ===
기술 중심 포지션 (백엔드, 시스템):
  → job_expertise 높게 (0.35-0.45)
  
협업 중심 포지션 (PM, 리드):
  → interpersonal_skill 높게 (0.20-0.30)
  
문제 해결 중심 (알고리즘, 최적화):
  → problem_solving 높게 (0.20-0.25)
  
스타트업/빠른 성장:
  → growth_potential 높게 (0.20-0.25)
  
문화/가치 강조:
  → organizational_fit 높게 (0.20-0.25)

=== 출력 형식 ===
{{
  "weights": {{
    "job_expertise": 0.35,
    "problem_solving": 0.20,
    "organizational_fit": 0.15,
    "growth_potential": 0.15,
    "interpersonal_skill": 0.10,
    "achievement_motivation": 0.05
  }},
  "reasoning": {{
    "job_expertise": "Python, AWS, PostgreSQL 등 구체적 기술 스택 다수 명시, 시스템 설계 경험 필수 요구사항",
    "problem_solving": "대용량 데이터 처리, 성능 최적화 등 복잡한 문제 해결 능력 강조",
    "organizational_fit": "스타트업 문화 언급은 있으나 구체적 가치관 명시 없음",
    "growth_potential": "빠른 학습 능력 우대 조건으로 언급",
    "interpersonal_skill": "협업 관련 내용 최소한으로만 언급",
    "achievement_motivation": "주도성 관련 키워드 부재"
  }},
  "position_type": "기술 중심 백엔드 개발자",
  "key_focus_areas": ["technical_depth", "system_design", "performance"]
}}

중요: 반드시 weights의 합이 정확히 1.0이 되도록 계산하세요.
"""
        return prompt