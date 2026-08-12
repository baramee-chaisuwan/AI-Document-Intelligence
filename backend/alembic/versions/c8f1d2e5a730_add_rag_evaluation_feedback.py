"""add rag evaluation feedback

Revision ID: c8f1d2e5a730
Revises: b7e2c9f4a610
Create Date: 2026-08-12
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c8f1d2e5a730"
down_revision: Union[str, Sequence[str], None] = "b7e2c9f4a610"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.add_column(
        "rag_evaluations",
        sa.Column(
            "retrieval_rating",
            sa.Integer(),
            nullable=True
        )
    )
    op.add_column(
        "rag_evaluations",
        sa.Column(
            "answer_rating",
            sa.Integer(),
            nullable=True
        )
    )
    op.add_column(
        "rag_evaluations",
        sa.Column(
            "feedback_note",
            sa.String(length=1000),
            nullable=True
        )
    )
    op.add_column(
        "rag_evaluations",
        sa.Column(
            "evaluated_at",
            sa.DateTime(timezone=True),
            nullable=True
        )
    )
    op.create_check_constraint(
        "ck_rag_evaluations_retrieval_rating",
        "rag_evaluations",
        (
            "retrieval_rating IS NULL OR "
            "retrieval_rating BETWEEN 1 AND 5"
        )
    )
    op.create_check_constraint(
        "ck_rag_evaluations_answer_rating",
        "rag_evaluations",
        (
            "answer_rating IS NULL OR "
            "answer_rating BETWEEN 1 AND 5"
        )
    )


def downgrade() -> None:

    op.drop_constraint(
        "ck_rag_evaluations_answer_rating",
        "rag_evaluations",
        type_="check"
    )
    op.drop_constraint(
        "ck_rag_evaluations_retrieval_rating",
        "rag_evaluations",
        type_="check"
    )
    op.drop_column(
        "rag_evaluations",
        "evaluated_at"
    )
    op.drop_column(
        "rag_evaluations",
        "feedback_note"
    )
    op.drop_column(
        "rag_evaluations",
        "answer_rating"
    )
    op.drop_column(
        "rag_evaluations",
        "retrieval_rating"
    )
