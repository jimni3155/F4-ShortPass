# server/services/applicant_service.py
"""
Applicant service for handling applicant-related business logic
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from models.interview import Applicant
from services.s3_service import S3Service


class ApplicantService:
    """지원자 관련 비즈니스 로직 처리"""

    def __init__(self):
        self.s3_service = S3Service()

    def create_applicant(
        self,
        db: Session,
        name: str,
        email: str,
        gender: Optional[str] = None,
        education: Optional[str] = None,
        birthdate: Optional[str] = None,
    ) -> Applicant:
        """
        지원자 생성 또는 업데이트 (Upsert)

        이메일이 중복되면 기존 지원자 정보를 업데이트합니다.

        Args:
            db: Database session
            name: 이름
            email: 이메일
            gender: 성별
            education: 학력
            birthdate: 생년월일

        Returns:
            Applicant: 생성 또는 업데이트된 지원자
        """
        # 생년월일에서 나이 계산 (선택)
        age = None
        if birthdate:
            try:
                birth_year = int(birthdate.split('-')[0])
                current_year = datetime.now().year
                age = current_year - birth_year
            except:
                pass

        # 이메일로 기존 지원자 확인
        existing_applicant = db.query(Applicant).filter(Applicant.email == email).first()

        if existing_applicant:
            # 기존 지원자 정보 업데이트
            existing_applicant.name = name
            if gender:
                existing_applicant.gender = gender
            if education:
                existing_applicant.education = education
            if age is not None:
                existing_applicant.age = age
            existing_applicant.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(existing_applicant)

            return existing_applicant
        else:
            # 새 지원자 생성
            applicant = Applicant(
                name=name,
                email=email,
                gender=gender,
                education=education,
                age=age,
            )

            db.add(applicant)
            db.commit()
            db.refresh(applicant)

            return applicant

    def upload_portfolio(
        self,
        db: Session,
        applicant_id: int,
        file_content: bytes,
        file_name: str
    ) -> str:
        """
        포트폴리오 PDF를 S3에 업로드하고 경로 저장

        Args:
            db: Database session
            applicant_id: 지원자 ID
            file_content: 파일 내용
            file_name: 파일명

        Returns:
            str: S3 파일 경로
        """
        applicant = db.query(Applicant).filter(Applicant.id == applicant_id).first()
        if not applicant:
            raise ValueError(f"Applicant {applicant_id} not found")

        # S3에 업로드
        # 폴더명을 portfolios/applicant_{id} 형식으로 지정
        s3_key = self.s3_service.upload_file(
            file_content=file_content,
            file_name=f"applicant_{applicant_id}_{file_name}",
            folder="portfolios"
        )

        # DB 업데이트
        applicant.portfolio_file_path = s3_key
        db.commit()
        db.refresh(applicant)

        return s3_key

    def get_applicant(self, db: Session, applicant_id: int) -> Optional[Applicant]:
        """
        지원자 조회

        Args:
            db: Database session
            applicant_id: 지원자 ID

        Returns:
            Optional[Applicant]: 지원자 정보
        """
        return db.query(Applicant).filter(Applicant.id == applicant_id).first()

    def get_applicants(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Applicant]:
        """
        지원자 목록 조회

        Args:
            db: Database session
            skip: 건너뛸 개수
            limit: 조회할 개수

        Returns:
            List[Applicant]: 지원자 목록
        """
        return db.query(Applicant).offset(skip).limit(limit).all()

    def update_applicant(
        self,
        db: Session,
        applicant_id: int,
        **kwargs
    ) -> Optional[Applicant]:
        """
        지원자 정보 수정

        Args:
            db: Database session
            applicant_id: 지원자 ID
            **kwargs: 수정할 필드들

        Returns:
            Optional[Applicant]: 수정된 지원자 정보
        """
        applicant = db.query(Applicant).filter(Applicant.id == applicant_id).first()
        if not applicant:
            return None

        for key, value in kwargs.items():
            if value is not None and hasattr(applicant, key):
                setattr(applicant, key, value)

        db.commit()
        db.refresh(applicant)

        return applicant

    def delete_applicant(self, db: Session, applicant_id: int) -> bool:
        """
        지원자 삭제

        Args:
            db: Database session
            applicant_id: 지원자 ID

        Returns:
            bool: 삭제 성공 여부
        """
        applicant = db.query(Applicant).filter(Applicant.id == applicant_id).first()
        if not applicant:
            return False

        db.delete(applicant)
        db.commit()

        return True
