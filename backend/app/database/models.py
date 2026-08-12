from datetime import (
    datetime,
    timezone
)

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    func,
    Index,
    Integer,
    JSON,
    String,
    Text,
    text,
    UniqueConstraint
)
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import JSONB

from app.database.database import Base
from app.models.candidate_stage import (
    CANDIDATE_STAGE_CHECK_SQL,
    CandidateStage
)
from app.models.processing_job_status import (
    PROCESSING_JOB_STATUS_CHECK_SQL,
    ProcessingJobStatus
)


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

    __table_args__ = (
        CheckConstraint(
            CANDIDATE_STAGE_CHECK_SQL,
            name="ck_candidates_candidate_stage"
        ),
        CheckConstraint(
            (
                "resume_sha256 IS NULL OR "
                "(length(resume_sha256) = 64 AND "
                "resume_sha256 = lower(resume_sha256))"
            ),
            name="ck_candidates_resume_sha256_format"
        ),
        Index(
            "ux_candidates_resume_sha256",
            "resume_sha256",
            unique=True,
            postgresql_where=text(
                "resume_sha256 IS NOT NULL"
            ),
            sqlite_where=text(
                "resume_sha256 IS NOT NULL"
            )
        ),
    )

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

    candidate_stage = Column(
        String(20),
        nullable=False,
        default=CandidateStage.APPLIED.value,
        server_default=CandidateStage.APPLIED.value
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

    resume_sha256 = Column(
        String(64),
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

    processing_jobs = relationship(
        "ResumeProcessingJob",
        back_populates="candidate",
        passive_deletes=True
    )


class ResumeProcessingJob(Base):

    __tablename__ = "resume_processing_jobs"

    __table_args__ = (
        CheckConstraint(
            PROCESSING_JOB_STATUS_CHECK_SQL,
            name=(
                "ck_resume_processing_jobs_status"
            )
        ),
        CheckConstraint(
            (
                "resume_sha256 IS NULL OR "
                "(length(resume_sha256) = 64 AND "
                "resume_sha256 = lower(resume_sha256))"
            ),
            name=(
                "ck_resume_processing_jobs_"
                "resume_sha256_format"
            )
        ),
        Index(
            "ix_resume_processing_jobs_status_created_at",
            "status",
            "created_at"
        ),
        Index(
            "ux_resume_processing_jobs_resume_sha256",
            "resume_sha256",
            unique=True,
            postgresql_where=text(
                "resume_sha256 IS NOT NULL"
            ),
            sqlite_where=text(
                "resume_sha256 IS NOT NULL"
            )
        ),
    )

    id = Column(
        Integer,
        primary_key=True
    )

    candidate_id = Column(
        Integer,
        ForeignKey(
            "candidates.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    status = Column(
        String(20),
        nullable=False,
        default=ProcessingJobStatus.PENDING.value,
        server_default=ProcessingJobStatus.PENDING.value
    )

    error_message = Column(
        Text,
        nullable=True
    )

    resume_sha256 = Column(
        String(64),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        server_default=func.now()
    )

    started_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
        server_default=func.now()
    )

    candidate = relationship(
        "Candidate",
        back_populates="processing_jobs"
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


class RAGEvaluation(Base):

    __tablename__ = "rag_evaluations"

    __table_args__ = (
        CheckConstraint(
            "operation IN ('assistant', 'recommendation')",
            name="ck_rag_evaluations_operation"
        ),
        CheckConstraint(
            "retrieved_count >= 0",
            name="ck_rag_evaluations_retrieved_count"
        ),
        CheckConstraint(
            (
                "retrieval_latency_ms >= 0 AND "
                "generation_latency_ms >= 0 AND "
                "total_latency_ms >= 0"
            ),
            name="ck_rag_evaluations_nonnegative_latency"
        ),
        Index(
            "ix_rag_evaluations_created_at",
            "created_at"
        ),
    )

    id = Column(
        Integer,
        primary_key=True
    )

    user_query = Column(
        Text,
        nullable=False
    )

    generated_answer = Column(
        Text,
        nullable=False
    )

    retrieved_documents = Column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=list
    )

    retrieval_latency_ms = Column(
        Float,
        nullable=False
    )

    generation_latency_ms = Column(
        Float,
        nullable=False
    )

    total_latency_ms = Column(
        Float,
        nullable=False
    )

    retrieved_count = Column(
        Integer,
        nullable=False,
        default=0
    )

    operation = Column(
        String(20),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        server_default=func.now()
    )
