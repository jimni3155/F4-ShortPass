#!/usr/bin/env python3
"""
실제 면접 데이터와 동일한 형태의 Mockup 데이터 생성 스크립트
"""
from sqlalchemy.orm import Session
from db.database import engine, get_db
from models.interview import InterviewSession, InterviewResult, InterviewStatus, Company
from models.job import Job
from datetime import datetime, timedelta
import random

def create_realistic_interview_data():
    """실제 면접 완료 데이터 생성"""

    db = next(get_db())

    try:
        # 0. Job 데이터가 없으면 생성
        job1 = db.query(Job).filter(Job.id == 1).first()
        if not job1:
            # Company도 확인
            company1 = db.query(Company).filter(Company.id == 1).first()
            if not company1:
                print("⚠️  Company ID 1이 없습니다. Company를 먼저 생성합니다.")
                company1 = Company(
                    id=1,
                    name="현대엘리베이터",
                    company_values_text="안전과 혁신을 최우선으로",
                    blind_mode=False
                )
                db.add(company1)
                db.flush()
                print(f"✓ Company 생성: {company1.name}")

            job1 = Job(
                id=1,
                company_id=1,
                title="엘리베이터 시스템 엔지니어",
                description="엘리베이터 기계 및 제어 시스템 설계·개발"
            )
            db.add(job1)

            job2 = Job(
                id=2,
                company_id=1,
                title="IoT 플랫폼 개발자",
                description="스마트 빌딩 IoT 플랫폼 개발"
            )
            db.add(job2)
            db.flush()
            print(f"✓ Job 생성: {job1.title}, {job2.title}")

        # 1. 기존 면접 세션을 COMPLETED로 변경
        session = db.query(InterviewSession).filter(InterviewSession.id == 1).first()
        if not session:
            print("❌ 면접 세션 1을 찾을 수 없습니다.")
            return

        session.status = InterviewStatus.COMPLETED
        session.started_at = datetime.utcnow() - timedelta(minutes=45)
        session.completed_at = datetime.utcnow()
        session.evaluation_completed = True

        print(f"✓ 면접 세션 {session.id} 상태를 COMPLETED로 변경")

        # 2. 실제같은 면접 결과 데이터 생성
        realistic_answers = [
            {
                "question_id": 1,
                "question_text": "엘리베이터 기계 구조 설계 시 고려해야 할 주요 요소는 무엇이며, 어떤 방식으로 설계하는지 설명해주세요.",
                "question_type": "technical",
                "is_common": False,
                "job_id": 1,
                "stt_full_text": """엘리베이터 기계 구조 설계 시 가장 중요한 요소는 안전성과 효율성입니다.
먼저 하중 계산을 통해 적절한 케이블 강도와 모터 용량을 결정해야 하고,
브레이크 시스템과 비상 정지 장치 같은 안전 장치를 필수적으로 설계에 포함시켜야 합니다.
또한 진동과 소음을 최소화하기 위한 완충 시스템도 중요하게 고려됩니다.
대학교 프로젝트에서 3층 규모의 엘리베이터 모형을 설계한 경험이 있으며,
CAD를 사용해 구조 설계를 하고 시뮬레이션을 통해 검증했습니다.""",
                "scores": {
                    "technical_depth": 85,
                    "problem_solving": 80,
                    "communication": 88,
                    "system_design": 82
                },
                "overall_score": 83.75,
                "keywords": {
                    "matched": ["안전성", "하중 계산", "CAD", "시뮬레이션"],
                    "missing": ["유압 시스템", "제어 알고리즘"]
                },
                "strengths": [
                    "안전성에 대한 명확한 이해",
                    "실제 프로젝트 경험 보유",
                    "체계적인 설계 접근법"
                ],
                "weaknesses": [
                    "고급 제어 시스템에 대한 설명 부족",
                    "최신 기술 트렌드 언급 부족"
                ],
                "ai_feedback": "엘리베이터 기계 구조의 핵심 요소들을 잘 이해하고 있으며, 실제 프로젝트 경험을 통해 실무적 지식을 갖추고 있습니다. 다만 IoT나 스마트 기술과의 연계에 대한 이해도를 높이면 더욱 좋을 것 같습니다."
            },
            {
                "question_id": 2,
                "question_text": "엘리베이터 제어 시스템 개발 시 고려해야 할 주요 요소는 무엇이며, 어떤 방식으로 개발하는지 설명해주세요.",
                "question_type": "technical",
                "is_common": False,
                "job_id": 1,
                "stt_full_text": """제어 시스템 개발에서는 실시간 응답성과 안전성이 가장 중요합니다.
PLC나 마이크로컨트롤러를 사용하여 센서 데이터를 실시간으로 처리하고,
각 층의 호출 버튼과 카 내부 버튼의 우선순위를 효율적으로 관리하는 알고리즘을 구현해야 합니다.
특히 비상 상황 발생 시 즉각적으로 대응할 수 있는 인터럽트 처리가 필수적입니다.
저는 Arduino와 C++을 활용한 제어 시스템 프로토타입을 개발해본 경험이 있으며,
다양한 센서와의 통신 프로토콜 구현에도 익숙합니다.""",
                "scores": {
                    "technical_depth": 88,
                    "programming_skill": 85,
                    "real_time_system": 82,
                    "problem_solving": 86
                },
                "overall_score": 85.25,
                "keywords": {
                    "matched": ["PLC", "실시간", "센서", "인터럽트", "C++"],
                    "missing": ["RTOS", "CAN 통신"]
                },
                "strengths": [
                    "실시간 시스템에 대한 이해도 높음",
                    "마이크로컨트롤러 개발 경험 보유",
                    "안전 시스템의 중요성 인지"
                ],
                "weaknesses": [
                    "산업용 표준 프로토콜 경험 부족",
                    "대규모 시스템 통합 경험 제한적"
                ],
                "ai_feedback": "제어 시스템의 핵심 개념을 잘 이해하고 있으며, 실습 경험을 통해 기초를 탄탄히 다진 것으로 보입니다. 산업 현장에서 사용되는 표준 프로토콜과 RTOS에 대한 학습을 추가하면 더욱 완벽할 것입니다."
            },
            {
                "question_id": 3,
                "question_text": "팀 프로젝트에서 어려움을 겪었던 경험과 해결 방법을 설명해주세요.",
                "question_type": "behavioral",
                "is_common": True,
                "job_id": None,
                "stt_full_text": """대학교 4학년 때 5명으로 구성된 팀에서 IoT 스마트홈 프로젝트를 진행했는데,
중간에 팀원 간 의견 충돌이 발생했습니다. 어떤 센서를 사용할지, 통신 프로토콜을 어떻게 구성할지에 대해
각자 다른 의견을 주장했고, 진행이 거의 멈췄던 적이 있었습니다.
저는 각 팀원의 의견을 정리하는 문서를 만들어 장단점을 객관적으로 비교했고,
실제 프로토타입을 간단히 만들어 테스트해보자고 제안했습니다.
결과적으로 실험을 통해 가장 효율적인 방법을 찾을 수 있었고,
모든 팀원이 납득할 수 있는 결론을 도출했습니다. 이 경험을 통해 기술적 의사결정에는
데이터와 실험이 중요하다는 것을 배웠습니다.""",
                "scores": {
                    "communication": 90,
                    "problem_solving": 88,
                    "teamwork": 92,
                    "leadership": 85
                },
                "overall_score": 88.75,
                "keywords": {
                    "matched": ["팀워크", "의견 충돌", "문제 해결", "데이터 기반"],
                    "missing": []
                },
                "strengths": [
                    "갈등 상황에서의 리더십 발휘",
                    "객관적이고 체계적인 문제 해결 접근",
                    "실험적 검증을 통한 의사결정"
                ],
                "weaknesses": [
                    "초기 대응이 다소 늦었음"
                ],
                "ai_feedback": "팀 내 갈등 상황을 건설적으로 해결한 경험이 인상적입니다. 특히 데이터와 실험을 통해 객관적인 의사결정을 이끌어낸 점이 훌륭합니다. 이러한 문제 해결 능력은 실무에서 매우 중요한 역량입니다."
            },
            {
                "question_id": 4,
                "question_text": "최근 관심 있는 기술 트렌드와 그것을 왜 중요하다고 생각하는지 설명해주세요.",
                "question_type": "behavioral",
                "is_common": True,
                "job_id": None,
                "stt_full_text": """최근에는 디지털 트윈 기술에 큰 관심을 가지고 있습니다.
엘리베이터나 물류 시스템 같은 물리적 설비를 가상 환경에서 시뮬레이션하고
실시간 데이터를 통해 최적화할 수 있다는 점이 매우 흥미롭습니다.
특히 예지 정비(Predictive Maintenance) 측면에서 센서 데이터와 AI를 결합하면
고장을 미리 예측하고 다운타임을 최소화할 수 있어
유지보수 비용을 크게 줄일 수 있다고 생각합니다.
관련 논문들을 찾아보면서 공부하고 있으며, 간단한 시뮬레이션 프로그램도 만들어보고 있습니다.""",
                "scores": {
                    "technical_curiosity": 92,
                    "industry_awareness": 88,
                    "learning_attitude": 90,
                    "vision": 85
                },
                "overall_score": 88.75,
                "keywords": {
                    "matched": ["디지털 트윈", "예지 정비", "AI", "최적화"],
                    "missing": []
                },
                "strengths": [
                    "최신 기술 트렌드에 대한 높은 관심",
                    "실무 적용 가능성 고려",
                    "자기주도적 학습 태도"
                ],
                "weaknesses": [
                    "실제 산업 적용 사례 경험 부족"
                ],
                "ai_feedback": "최신 기술 트렌드에 대한 관심과 이해도가 높으며, 실무적 가치를 염두에 두고 학습하는 자세가 돋보입니다. 디지털 트윈과 AI의 결합은 향후 스마트 팩토리에서 핵심 기술이 될 것으로 예상됩니다."
            },
            {
                "question_id": 5,
                "question_text": "5년 후 자신의 모습을 어떻게 그리고 있는지 설명해주세요.",
                "question_type": "behavioral",
                "is_common": True,
                "job_id": None,
                "stt_full_text": """5년 후에는 엘리베이터나 물류 자동화 시스템 분야의 전문 엔지니어로 성장해 있고 싶습니다.
단순히 기술적인 역량뿐만 아니라, 고객의 요구사항을 정확히 파악하고
최적의 솔루션을 제안할 수 있는 문제 해결 능력을 갖춘 엔지니어가 되고 싶습니다.
또한 후배 엔지니어들을 멘토링하면서 팀의 기술력 향상에도 기여하고 싶고,
가능하다면 특허 출원이나 기술 논문 발표 같은 활동을 통해
회사의 기술 경쟁력 강화에도 일조하고 싶습니다.
그리고 무엇보다 안전하고 효율적인 시스템을 만들어서
사람들의 일상을 더 편리하게 만드는 일에 보람을 느끼는 엔지니어가 되고 싶습니다.""",
                "scores": {
                    "career_vision": 88,
                    "growth_mindset": 90,
                    "company_fit": 92,
                    "motivation": 89
                },
                "overall_score": 89.75,
                "keywords": {
                    "matched": ["전문성", "문제 해결", "멘토링", "기술 경쟁력"],
                    "missing": []
                },
                "strengths": [
                    "명확하고 현실적인 커리어 비전",
                    "기술적 성장과 팀 기여의 균형",
                    "회사와의 높은 적합도"
                ],
                "weaknesses": [
                    "구체적인 단기 목표 설정 필요"
                ],
                "ai_feedback": "장기적인 커리어 비전이 명확하고 회사의 비전과도 잘 부합합니다. 기술 전문성과 팀워크, 사회적 가치를 모두 고려하는 균형잡힌 시각이 인상적입니다."
            }
        ]

        # 3. InterviewResult 데이터 삽입
        for answer_data in realistic_answers:
            result = InterviewResult(
                interview_id=session.id,
                question_id=answer_data["question_id"],
                question_text=answer_data["question_text"],
                question_type=answer_data["question_type"],
                is_common=answer_data["is_common"],
                job_id=answer_data["job_id"],
                stt_full_text=answer_data["stt_full_text"],
                scores=answer_data["scores"],
                overall_score=answer_data["overall_score"],
                keywords=answer_data["keywords"],
                strengths=answer_data["strengths"],
                weaknesses=answer_data["weaknesses"],
                ai_feedback=answer_data["ai_feedback"]
            )
            db.add(result)
            print(f"✓ 질문 {answer_data['question_id']} 답변 추가")

        db.commit()
        print("\n" + "="*60)
        print("✅ 실제 면접 데이터 생성 완료!")
        print("="*60)
        print(f"면접 세션 ID: {session.id}")
        print(f"지원자 ID: {session.applicant_id}")
        print(f"회사 IDs: {session.job_ids}")
        print(f"답변 수: {len(realistic_answers)}개")
        print(f"평균 점수: {sum(a['overall_score'] for a in realistic_answers) / len(realistic_answers):.2f}")
        print("="*60)

    except Exception as e:
        db.rollback()
        print(f"❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    create_realistic_interview_data()
