from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from app.database.database import Base
from sqlalchemy import DateTime
from datetime import datetime


class Candidate(Base):

    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String)

    summary = Column(Text)

    candidate_level = Column(String)

    skill_score = Column(Integer)

    created_at = Column(DateTime,default=datetime.utcnow)