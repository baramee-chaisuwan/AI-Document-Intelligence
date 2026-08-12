"""add rag evaluations

Revision ID: b7e2c9f4a610
Revises: a3d8c6e1f520
Create Date: 2026-08-12
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "b7e2c9f4a610"
down_revision: Union[str, Sequence[str], None] = "a3d8c6e1f520"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        "rag_evaluations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_query", sa.Text(), nullable=False),
        sa.Column("generated_answer", sa.Text(), nullable=False),
        sa.Column(
            "retrieved_documents",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False
        ),
        sa.Column("retrieval_latency_ms", sa.Float(), nullable=False),
        sa.Column("generation_latency_ms", sa.Float(), nullable=False),
        sa.Column("total_latency_ms", sa.Float(), nullable=False),
        sa.Column("retrieved_count", sa.Integer(), nullable=False),
        sa.Column("operation", sa.String(length=20), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False
        ),
        sa.CheckConstraint(
            "operation IN ('assistant', 'recommendation')",
            name="ck_rag_evaluations_operation"
        ),
        sa.CheckConstraint(
            "retrieved_count >= 0",
            name="ck_rag_evaluations_retrieved_count"
        ),
        sa.CheckConstraint(
            (
                "retrieval_latency_ms >= 0 AND "
                "generation_latency_ms >= 0 AND "
                "total_latency_ms >= 0"
            ),
            name="ck_rag_evaluations_nonnegative_latency"
        ),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index(
        "ix_rag_evaluations_created_at",
        "rag_evaluations",
        ["created_at"],
        unique=False
    )


def downgrade() -> None:

    op.drop_index(
        "ix_rag_evaluations_created_at",
        table_name="rag_evaluations"
    )
    op.drop_table("rag_evaluations")
