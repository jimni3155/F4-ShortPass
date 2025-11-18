from sqlalchemy import Column, Integer, String, Boolean, JSON
from db.database import Base

class Company(Base):
    __tablename__ = "companies"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    size = Column(String)
    jd = Column(JSON)  # duties, requirements, preferred를 JSON으로 저장
    values = Column(String)
    questions = Column(JSON)  # 질문 리스트를 JSON으로 저장
    blind = Column(Boolean, default=False)