# create_test_persona_instances.py
"""
테스트용 페르소나 인스턴스 생성 스크립트

실행 방법:
    python create_test_persona_instances.py
"""

from sqlalchemy.orm import Session
from db.database import SessionLocal
from models.interview import PersonaInstance, PersonaDB, Company


def create_test_persona_instances():
    """테스트용 페르소나 인스턴스 생성"""
    db: Session = SessionLocal()

    try:
        print("=" * 60)
        print("테스트 페르소나 인스턴스 생성 시작")
        print("=" * 60)

        # 1. 회사 조회
        companies = db.query(Company).limit(3).all()
        if not companies:
            print("❌ 회사 데이터가 없습니다. 먼저 회사 데이터를 생성하세요.")
            return

        print(f"\n조회된 회사: {len(companies)}개")

        # 2. 페르소나 템플릿 조회
        personas = db.query(PersonaDB).limit(3).all()
        if not personas:
            print("❌ 페르소나 템플릿이 없습니다. 먼저 페르소나를 생성하세요.")
            return

        print(f"조회된 페르소나 템플릿: {len(personas)}개")

        # 3. 각 회사별 페르소나 인스턴스 생성
        for company in companies:
            print(f"\n[회사: {company.name}]")

            # 기술형 페르소나
            instance_1 = PersonaInstance(
                company_id=company.id,
                persona_template_id=personas[0].id if len(personas) > 0 else 1,
                instance_name="기술형",
                custom_weights={"technical": 0.4, "logic": 0.3, "culture": 0.3},
                question_tone="기술적 깊이를 중시하며 구체적인 경험을 묻습니다."
            )
            db.add(instance_1)
            print(f"   ✓ 페르소나 인스턴스 생성: 기술형")

            # 논리형 페르소나
            instance_2 = PersonaInstance(
                company_id=company.id,
                persona_template_id=personas[1].id if len(personas) > 1 else 1,
                instance_name="논리형",
                custom_weights={"technical": 0.3, "logic": 0.4, "culture": 0.3},
                question_tone="논리적 사고와 문제 해결 능력을 평가합니다."
            )
            db.add(instance_2)
            print(f"   ✓ 페르소나 인스턴스 생성: 논리형")

            # 컬처핏형 페르소나
            instance_3 = PersonaInstance(
                company_id=company.id,
                persona_template_id=personas[2].id if len(personas) > 2 else 1,
                instance_name="컬처핏형",
                custom_weights={"technical": 0.2, "logic": 0.3, "culture": 0.5},
                question_tone="조직 문화 적합성과 협업 능력을 중시합니다."
            )
            db.add(instance_3)
            print(f"   ✓ 페르소나 인스턴스 생성: 컬처핏형")

        db.commit()

        # 4. 생성 결과 확인
        total_instances = db.query(PersonaInstance).count()
        print("\n" + "=" * 60)
        print(f"✅ 페르소나 인스턴스 생성 완료!")
        print(f"   총 {total_instances}개 생성됨")
        print("=" * 60)

        # 생성된 인스턴스 목록 출력
        print("\n[생성된 페르소나 인스턴스 목록]")
        instances = db.query(PersonaInstance).all()
        for instance in instances:
            company = db.query(Company).filter(Company.id == instance.company_id).first()
            print(f"   ID: {instance.id} | 회사: {company.name} | 이름: {instance.instance_name}")

    except Exception as e:
        db.rollback()
        print(f"\n❌ 에러 발생: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    create_test_persona_instances()
