from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    JSON,
    String,
    Text
)

from app.database.database import Base


class Candidate(Base):

    __tablename__ = "candidates"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(255),
        nullable=False,
        index=True
    )

    summary = Column(
        Text,
        nullable=False
    )

    candidate_level = Column(
        String(50),
        nullable=False
    )

    skill_score = Column(
        Integer,
        nullable=False,
        default=0
    )

    rule_score = Column(
        Integer,
        nullable=False,
        default=0
    )

    ai_score = Column(
        Integer,
        nullable=False,
        default=0
    )

    ai_status = Column(
        String(20),
        nullable=False,
        default="success"
    )

    score_breakdown = Column(
        JSON,
        nullable=False,
        default=dict
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )