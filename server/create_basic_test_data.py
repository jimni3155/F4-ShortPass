# create_basic_test_data.py
"""기본 테스트 데이터 생성"""

from sqlalchemy.orm import Session
from db.database import SessionLocal, Base, engine
from models.interview import Company, Applicant, PersonaDB, PersonaInstance
from datetime import datetime


def create_basic_test_data():
    """기본 테스트 데이터 생성"""

    # 테이블 생성
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()

    try:
        print("=" * 60)
        print("기본 테스트 데이터 생성 시작")
        print("=" * 60)

        # 1. 회사 생성
        print("\n[1/3] 회사 생성 중...")
        company = Company(
            name="테크 스타트업",
            company_values_text="혁신과 도전을 추구하는 기업",
            company_culture_desc="수평적이고 자유로운 조직 문화",
            core_values=["혁신", "도전", "협업"],
            category_weights={"기술": 0.4, "태도": 0.3, "경험": 0.3},
            blind_mode=False
        )
        db.add(company)
        db.commit()
        db.refresh(company)
        print(f"   ✓ 회사 생성: {company.name} (ID: {company.id})")

        # 2. 지원자 생성
        print("\n[2/3] 지원자 생성 중...")
        applicant = Applicant(
            name="홍길동",
            email="hong@example.com",
            age=28,
            education="서울대학교 컴퓨터공학과",
            gender="남성",
            skills=["Python", "FastAPI", "React"],
            total_experience_years=3
        )
        db.add(applicant)
        db.commit()
        db.refresh(applicant)
        print(f"   ✓ 지원자 생성: {applicant.name} (ID: {applicant.id})")

        # 3. 페르소나 템플릿 생성
        print("\n[3/3] 페르소나 템플릿 생성 중...")
        personas_data = [
            {
                "company_id": company.id,
                "persona_name": "기술 면접관",
                "archetype": "analytical",
                "description": "기술적 깊이를 평가하는 면접관",
                "system_prompt": "당신은 기술적 역량을 평가하는 면접관입니다.",
                "welcome_message": "안녕하세요. 기술 면접을 진행하겠습니다.",
                "focus_keywords": ["Python", "FastAPI", "시스템 설계"],
                "focus_areas": ["기술 역량", "문제 해결"]
            },
            {
                "company_id": company.id,
                "persona_name": "논리 면접관",
                "archetype": "analytical",
                "description": "논리적 사고를 평가하는 면접관",
                "system_prompt": "당신은 논리적 사고를 평가하는 면접관입니다.",
                "welcome_message": "안녕하세요. 논리 면접을 진행하겠습니다.",
                "focus_keywords": ["논리", "문제 해결", "의사 결정"],
                "focus_areas": ["논리적 사고", "판단력"]
            },
            {
                "company_id": company.id,
                "persona_name": "컬처핏 면접관",
                "archetype": "supportive",
                "description": "조직 문화 적합성을 평가하는 면접관",
                "system_prompt": "당신은 조직 문화 적합성을 평가하는 면접관입니다.",
                "welcome_message": "안녕하세요. 컬처핏 면접을 진행하겠습니다.",
                "focus_keywords": ["협업", "커뮤니케이션", "가치관"],
                "focus_areas": ["문화 적합성", "팀워크"]
            }
        ]

        created_personas = []
        for p_data in personas_data:
            persona = PersonaDB(**p_data)
            db.add(persona)
            created_personas.append(persona)

        db.commit()

        for persona in created_personas:
            db.refresh(persona)
            print(f"   ✓ 페르소나 템플릿 생성: {persona.persona_name} (ID: {persona.id})")

        # 4. 페르소나 인스턴스 생성
        print("\n[4/4] 페르소나 인스턴스 생성 중...")
        instance_data = [
            {
                "name": "기술형",
                "template": created_personas[0],
                "weights": {"technical": 0.4, "logic": 0.3, "culture": 0.3}
            },
            {
                "name": "논리형",
                "template": created_personas[1],
                "weights": {"technical": 0.3, "logic": 0.4, "culture": 0.3}
            },
            {
                "name": "컬처핏형",
                "template": created_personas[2],
                "weights": {"technical": 0.2, "logic": 0.3, "culture": 0.5}
            }
        ]

        created_instances = []
        for inst in instance_data:
            instance = PersonaInstance(
                company_id=company.id,
                persona_template_id=inst["template"].id,
                instance_name=inst["name"],
                custom_weights=inst["weights"],
                question_tone=f"{inst['name']} 관점에서 질문합니다."
            )
            db.add(instance)
            created_instances.append(instance)

        db.commit()

        for instance in created_instances:
            db.refresh(instance)
            print(f"   ✓ 페르소나 인스턴스 생성: {instance.instance_name} (ID: {instance.id})")

        print("\n" + "=" * 60)
        print("✅ 기본 테스트 데이터 생성 완료!")
        print("=" * 60)
        print(f"\n회사 ID: {company.id}")
        print(f"지원자 ID: {applicant.id}")
        print(f"페르소나 인스턴스 IDs: {[i.id for i in created_instances]}")
        print("\n사용 예시:")
        print(f'POST /interviews/prepare')
        print(f'{{"candidateId": "{applicant.id}", "companyId": "{company.id}", "personaInstanceIds": {[str(i.id) for i in created_instances]}}}')

    except Exception as e:
        db.rollback()
        print(f"\n❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    create_basic_test_data()
