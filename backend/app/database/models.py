from datetime import (
    datetime,
    timezone
)

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Integer,
    JSON,
    String,
    Text
)

from app.database.database import Base


def utc_now():

    return datetime.now(
        timezone.utc
    )


class User(Base):

    __tablename__ = "users"

    __table_args__ = (
        CheckConstraint(
            "role IN ('admin', 'recruiter')",
            name="ck_users_role"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    email = Column(
        String(320),
        nullable=False,
        unique=True,
        index=True
    )

    full_name = Column(
        String(255),
        nullable=False
    )

    hashed_password = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(20),
        nullable=False,
        default="recruiter"
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now
    )


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

    resume_s3_key = Column(
        String(1024),
        nullable=True
    )

    resume_filename = Column(
        String(255),
        nullable=True
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
