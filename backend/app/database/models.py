from sqlalchemy import Column, Integer, String, Text, JSON, DateTime
from app.database.database import Base
from datetime import datetime

class Candidate(Base):

    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String)

    summary = Column(Text)

    candidate_level = Column(String)

    skill_score = Column(Integer)

    created_at = Column(DateTime,default=datetime.utcnow)

    score_breakdown = Column(JSON, nullable=True)

    rule_score = Column(Integer, default=0)

    ai_score = Column(Integer, default=0)

    ai_status = Column(String, default="success")