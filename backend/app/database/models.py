from datetime import (
    datetime,
    timezone
)

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint
)
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

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

    token_version = Column(
        Integer,
        nullable=False,
        default=0
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

    password_reset_tokens = relationship(
        "PasswordResetToken",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    jobs = relationship(
        "Job",
        back_populates="creator"
    )


class PasswordResetToken(Base):

    __tablename__ = "password_reset_tokens"

    __table_args__ = (
        CheckConstraint(
            "failed_attempts >= 0",
            name="ck_password_reset_tokens_failed_attempts"
        ),
        Index(
            "ix_password_reset_tokens_user_created",
            "user_id",
            "created_at"
        ),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    otp_hash = Column(String(255), nullable=False)
    expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now
    )
    verified_at = Column(DateTime(timezone=True), nullable=True)
    consumed_at = Column(DateTime(timezone=True), nullable=True)
    invalidated_at = Column(DateTime(timezone=True), nullable=True)
    failed_attempts = Column(Integer, nullable=False, default=0)

    user = relationship(
        "User",
        back_populates="password_reset_tokens"
    )


def empty_job_requirements():

    return {
        "required_skills": [],
        "preferred_skills": [],
        "experience_requirements": [],
        "responsibilities": []
    }


class Job(Base):

    __tablename__ = "jobs"

    id = Column(
        Integer,
        primary_key=True
    )

    title = Column(
        String(255),
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    extracted_requirements = Column(
        JSON,
        nullable=False,
        default=empty_job_requirements
    )

    embedding = Column(
        Vector(384),
        nullable=True
    )

    created_by = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="RESTRICT"
        ),
        nullable=False,
        index=True
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now
    )

    creator = relationship(
        "User",
        back_populates="jobs"
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

    resume_storage_key = Column(
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

    resume_chunks = relationship(
        "ResumeChunk",
        back_populates="candidate",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


class ResumeChunk(Base):

    __tablename__ = "resume_chunks"

    __table_args__ = (
        CheckConstraint(
            "chunk_index >= 0",
            name="ck_resume_chunks_chunk_index"
        ),
        UniqueConstraint(
            "candidate_id",
            "chunk_index",
            name="uq_resume_chunks_candidate_chunk"
        ),
        Index(
            "ix_resume_chunks_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={
                "embedding": "vector_cosine_ops"
            }
        )
    )

    id = Column(
        Integer,
        primary_key=True
    )

    candidate_id = Column(
        Integer,
        ForeignKey(
            "candidates.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    document_id = Column(
        String(255),
        nullable=False,
        unique=True
    )

    chunk_index = Column(
        Integer,
        nullable=False
    )

    chunk_text = Column(
        Text,
        nullable=False
    )

    embedding = Column(
        Vector(384),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now
    )

    candidate = relationship(
        "Candidate",
        back_populates="resume_chunks"
    )
