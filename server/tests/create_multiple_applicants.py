#!/usr/bin/env python3
"""
여러 명의 지원자 면접 결과 mockup 데이터 생성
"""
import sys
import os
from datetime import datetime, timezone

# 프로젝트 루트를 Python path에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from db.database import SessionLocal, engine
from models.interview import Company, Applicant, InterviewSession, InterviewResult, InterviewStatus
from models.job import Job

def create_applicants_data():
    """6명의 지원자 면접 결과 데이터 생성"""
    db: Session = SessionLocal()

    try:
        print("\n" + "="*60)
        print("여러 지원자 면접 결과 데이터 생성")
        print("="*60 + "\n")

        # 1. Job & Company 확인 (이미 생성되어 있음)
        job = db.query(Job).filter(Job.id == 1).first()
        if not job:
            print("❌ Job ID 1이 존재하지 않습니다.")
            return

        company = db.query(Company).filter(Company.id == job.company_id).first()
        if not company:
            print("❌ Company를 찾을 수 없습니다.")
            return

        print(f"✓ Job: {job.title} (ID: {job.id})")
        print(f"✓ Company: {company.name} (ID: {company.id})\n")

        # 2. 6명의 지원자 데이터
        applicants_data = [
            {
                "name": "윤지원",
                "email": "yoon.jiwon@example.com",
                "age": 28,
                "education": "서울대학교 컴퓨터공학과",
                "gender": "여성",
                "skills": ["Python", "FastAPI", "React", "PostgreSQL", "AWS"],
                "total_experience_years": 5,
                "domain_experience": ["백엔드 개발", "클라우드 인프라"],
                "special_experience": ["MSA 아키텍처 설계", "대용량 트래픽 처리"],
                "scores": {
                    "python": 92,
                    "fastapi": 90,
                    "postgresql": 88,
                    "system_design": 91,
                    "problem_solving": 89,
                    "communication": 90
                },
                "overall_score": 90.0,
                "strengths": [
                    "뛰어난 기술 역량과 시스템 설계 능력",
                    "대규모 프로젝트 경험 풍부",
                    "명확한 커뮤니케이션"
                ],
                "weaknesses": [
                    "팀 리드 경험 부족"
                ]
            },
            {
                "name": "백수민",
                "email": "baek.sumin@example.com",
                "age": 26,
                "education": "연세대학교 소프트웨어학과",
                "gender": "여성",
                "skills": ["Python", "Django", "Vue.js", "MySQL", "Docker"],
                "total_experience_years": 3,
                "domain_experience": ["풀스택 개발", "DevOps"],
                "special_experience": ["CI/CD 파이프라인 구축"],
                "scores": {
                    "python": 85,
                    "react": 86,
                    "postgresql": 84,
                    "system_design": 83,
                    "problem_solving": 87,
                    "communication": 88
                },
                "overall_score": 85.5,
                "strengths": [
                    "풀스택 개발 능력",
                    "빠른 학습 능력",
                    "적극적인 커뮤니케이션"
                ],
                "weaknesses": [
                    "대규모 시스템 경험 부족",
                    "아키텍처 설계 경험 필요"
                ]
            },
            {
                "name": "정지은",
                "email": "jung.jieun@example.com",
                "age": 30,
                "education": "KAIST 전산학부",
                "gender": "여성",
                "skills": ["Python", "Go", "Kubernetes", "MongoDB", "Redis"],
                "total_experience_years": 7,
                "domain_experience": ["백엔드 개발", "데이터 엔지니어링"],
                "special_experience": ["분산 시스템 설계", "성능 최적화"],
                "scores": {
                    "python": 95,
                    "kubernetes": 94,
                    "postgresql": 90,
                    "system_design": 93,
                    "problem_solving": 92,
                    "communication": 85
                },
                "overall_score": 91.5,
                "strengths": [
                    "최고 수준의 기술 역량",
                    "분산 시스템 전문가",
                    "문제 해결 능력 탁월"
                ],
                "weaknesses": [
                    "커뮤니케이션 스타일 개선 필요"
                ]
            },
            {
                "name": "김지민",
                "email": "kim.jimin@example.com",
                "age": 24,
                "education": "고려대학교 컴퓨터학과",
                "gender": "남성",
                "skills": ["Python", "JavaScript", "Node.js", "PostgreSQL"],
                "total_experience_years": 2,
                "domain_experience": ["백엔드 개발"],
                "special_experience": ["RESTful API 설계"],
                "scores": {
                    "python": 78,
                    "javascript": 80,
                    "postgresql": 77,
                    "problem_solving": 80,
                    "communication": 85
                },
                "overall_score": 80.0,
                "strengths": [
                    "기본기 탄탄",
                    "학습 의욕 높음",
                    "좋은 커뮤니케이션"
                ],
                "weaknesses": [
                    "실무 경험 부족",
                    "기술 깊이 보완 필요",
                    "복잡한 시스템 설계 경험 필요"
                ]
            },
            {
                "name": "하지민",
                "email": "ha.jimin@example.com",
                "age": 27,
                "education": "성균관대학교 소프트웨어학과",
                "gender": "여성",
                "skills": ["Python", "Flask", "React", "MySQL", "AWS"],
                "total_experience_years": 4,
                "domain_experience": ["백엔드 개발", "프론트엔드 개발"],
                "special_experience": ["스타트업 초기 멤버 경험"],
                "scores": {
                    "python": 82,
                    "react": 85,
                    "postgresql": 81,
                    "problem_solving": 84,
                    "communication": 90
                },
                "overall_score": 84.4,
                "strengths": [
                    "균형 잡힌 기술 역량",
                    "뛰어난 커뮤니케이션",
                    "스타트업 경험"
                ],
                "weaknesses": [
                    "대규모 시스템 경험 부족",
                    "특화된 전문성 개발 필요"
                ]
            },
            {
                "name": "김도연",
                "email": "kim.doyeon@example.com",
                "age": 29,
                "education": "이화여자대학교 컴퓨터공학과",
                "gender": "여성",
                "skills": ["Python", "FastAPI", "TypeScript", "PostgreSQL", "GraphQL"],
                "total_experience_years": 6,
                "domain_experience": ["백엔드 개발", "API 설계"],
                "special_experience": ["팀 리드 경험", "기술 멘토링"],
                "scores": {
                    "python": 88,
                    "fastapi": 89,
                    "postgresql": 87,
                    "system_design": 87,
                    "problem_solving": 90,
                    "communication": 92
                },
                "overall_score": 88.8,
                "strengths": [
                    "리더십과 기술력의 조화",
                    "멘토링 경험 풍부",
                    "뛰어난 커뮤니케이션"
                ],
                "weaknesses": [
                    "최신 기술 트렌드 학습 필요"
                ]
            }
        ]

        # 3. 각 지원자별로 Applicant, InterviewSession, InterviewResult 생성
        for idx, applicant_info in enumerate(applicants_data, start=1):
            print(f"\n📋 지원자 {idx}: {applicant_info['name']}")

            # Applicant 생성 또는 조회
            applicant = db.query(Applicant).filter(Applicant.email == applicant_info['email']).first()
            if not applicant:
                applicant = Applicant(
                    name=applicant_info['name'],
                    email=applicant_info['email'],
                    age=applicant_info['age'],
                    education=applicant_info['education'],
                    gender=applicant_info['gender'],
                    skills=applicant_info['skills'],
                    total_experience_years=applicant_info['total_experience_years'],
                    domain_experience=applicant_info['domain_experience'],
                    special_experience=applicant_info['special_experience']
                )
                db.add(applicant)
                db.flush()
                print(f"  ✓ Applicant 생성: {applicant.name} (ID: {applicant.id})")
            else:
                print(f"  ✓ Applicant 기존 사용: {applicant.name} (ID: {applicant.id})")

            # InterviewSession 생성 (COMPLETED)
            completed_time = datetime.now(timezone.utc)
            session = InterviewSession(
                applicant_id=applicant.id,
                job_ids=[job.id],
                status=InterviewStatus.COMPLETED,
                current_question_index=5,
                started_at=completed_time,
                completed_at=completed_time,
                evaluation_completed=True
            )
            db.add(session)
            db.flush()
            print(f"  ✓ InterviewSession 생성: ID {session.id} (COMPLETED)")

            # InterviewResult 생성 (5개 질문)
            questions = [
                {
                    "question_id": 1 + (idx-1)*10,
                    "question_text": f"엘리베이터 기계 구조 설계 시 안전성을 최우선으로 고려해야 하는 이유는?",
                    "question_type": "technical",
                    "is_common": False,
                    "answer": f"{applicant_info['name']}의 답변: 엘리베이터 안전성은 사람의 생명과 직결되기 때문에 가장 중요합니다. 브레이크 시스템, 비상정지 장치, 과부하 방지 시스템 등이 필수적이며..."
                },
                {
                    "question_id": 2 + (idx-1)*10,
                    "question_text": "IoT 센서를 활용한 예지보전 시스템 구축 경험이 있나요?",
                    "question_type": "technical",
                    "is_common": False,
                    "answer": f"{applicant_info['name']}의 답변: 네, 이전 프로젝트에서 센서 데이터를 수집하고 분석하여 장비 이상을 사전에 감지하는 시스템을 구축했습니다. MQTT 프로토콜을 사용하여..."
                },
                {
                    "question_id": 3 + (idx-1)*10,
                    "question_text": "팀 프로젝트에서 의견 충돌이 있을 때 어떻게 해결하시나요?",
                    "question_type": "behavioral",
                    "is_common": True,
                    "answer": f"{applicant_info['name']}의 답변: 먼저 상대방의 의견을 경청하고 이해하려 노력합니다. 데이터와 객관적인 근거를 바탕으로 논의하며, 공동의 목표를 상기시키며..."
                },
                {
                    "question_id": 4 + (idx-1)*10,
                    "question_text": "가장 어려웠던 기술적 문제와 해결 방법은?",
                    "question_type": "behavioral",
                    "is_common": True,
                    "answer": f"{applicant_info['name']}의 답변: 대용량 트래픽 처리 시 발생한 성능 이슈가 가장 어려웠습니다. 캐싱 전략을 개선하고 데이터베이스 쿼리를 최적화하여..."
                },
                {
                    "question_id": 5 + (idx-1)*10,
                    "question_text": "우리 회사에서 이루고 싶은 목표는 무엇인가요?",
                    "question_type": "cultural",
                    "is_common": True,
                    "answer": f"{applicant_info['name']}의 답변: 엘리베이터 산업의 디지털 전환을 이끄는 엔지니어로 성장하고 싶습니다. 안전하고 효율적인 시스템을 통해 사람들의 일상에 기여하고..."
                }
            ]

            for q in questions:
                result = InterviewResult(
                    interview_id=session.id,
                    question_id=q["question_id"],
                    question_text=q["question_text"],
                    question_type=q["question_type"],
                    is_common=q["is_common"],
                    job_id=job.id if not q["is_common"] else None,
                    stt_full_text=q["answer"],
                    scores=applicant_info["scores"],
                    overall_score=applicant_info["overall_score"],
                    keywords={"matched": applicant_info["skills"][:3], "missing": []},
                    strengths=applicant_info["strengths"],
                    weaknesses=applicant_info["weaknesses"],
                    ai_feedback=f"{applicant_info['name']}님의 답변은 {applicant_info['overall_score']}점으로 평가됩니다. " + " ".join(applicant_info["strengths"])
                )
                db.add(result)

            print(f"  ✓ InterviewResult 5개 생성")

        # 4. 커밋
        db.commit()

        print("\n" + "="*60)
        print(f"✅ 6명의 지원자 데이터 생성 완료!")
        print("="*60 + "\n")

        # 생성된 데이터 요약
        print("📊 생성된 지원자 요약:")
        print("-" * 60)
        for applicant_info in applicants_data:
            print(f"  • {applicant_info['name']:<8} | 점수: {applicant_info['overall_score']:<6.2f} | 경력: {applicant_info['total_experience_years']}년 | {applicant_info['education']}")
        print("-" * 60)

    except Exception as e:
        db.rollback()
        print(f"\n❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    create_applicants_data()
