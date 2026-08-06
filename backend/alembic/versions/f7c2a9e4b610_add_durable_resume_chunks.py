"""add durable resume chunks with pgvector

Revision ID: f7c2a9e4b610
Revises: e6b1c4d8a2f7
Create Date: 2026-08-06
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


revision: str = "f7c2a9e4b610"
down_revision: Union[
    str,
    Sequence[str],
    None
] = "e6b1c4d8a2f7"
branch_labels: Union[
    str,
    Sequence[str],
    None
] = None
depends_on: Union[
    str,
    Sequence[str],
    None
] = None


def upgrade() -> None:

    op.execute(
        "CREATE EXTENSION IF NOT EXISTS vector"
    )

    op.create_table(
        "resume_chunks",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "candidate_id",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "document_id",
            sa.String(length=255),
            nullable=False
        ),
        sa.Column(
            "chunk_index",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "chunk_text",
            sa.Text(),
            nullable=False
        ),
        sa.Column(
            "embedding",
            Vector(384),
            nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False
        ),
        sa.CheckConstraint(
            "chunk_index >= 0",
            name="ck_resume_chunks_chunk_index"
        ),
        sa.ForeignKeyConstraint(
            ["candidate_id"],
            ["candidates.id"],
            name="fk_resume_chunks_candidate_id_candidates",
            ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name="pk_resume_chunks"
        ),
        sa.UniqueConstraint(
            "candidate_id",
            "chunk_index",
            name="uq_resume_chunks_candidate_chunk"
        ),
        sa.UniqueConstraint(
            "document_id",
            name="uq_resume_chunks_document_id"
        )
    )

    op.create_index(
        "ix_resume_chunks_candidate_id",
        "resume_chunks",
        ["candidate_id"],
        unique=False
    )

    op.create_index(
        "ix_resume_chunks_embedding_hnsw",
        "resume_chunks",
        ["embedding"],
        unique=False,
        postgresql_using="hnsw",
        postgresql_ops={
            "embedding": "vector_cosine_ops"
        }
    )


def downgrade() -> None:

    op.drop_index(
        "ix_resume_chunks_embedding_hnsw",
        table_name="resume_chunks",
        postgresql_using="hnsw"
    )

    op.drop_index(
        "ix_resume_chunks_candidate_id",
        table_name="resume_chunks"
    )

    op.drop_table(
        "resume_chunks"
    )

    # The vector extension is intentionally retained because it is a
    # database-level capability that may be shared by other schemas.
