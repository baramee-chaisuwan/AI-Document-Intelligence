"""add resume sha256 deduplication

Revision ID: a3d8c6e1f520
Revises: f4a6c8e2d190
Create Date: 2026-08-12
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a3d8c6e1f520"
down_revision: Union[str, Sequence[str], None] = "f4a6c8e2d190"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.add_column(
        "candidates",
        sa.Column(
            "resume_sha256",
            sa.String(length=64),
            nullable=True
        )
    )
    op.create_check_constraint(
        "ck_candidates_resume_sha256_format",
        "candidates",
        (
            "resume_sha256 IS NULL OR "
            "resume_sha256 ~ '^[0-9a-f]{64}$'"
        )
    )
    op.create_index(
        "ux_candidates_resume_sha256",
        "candidates",
        ["resume_sha256"],
        unique=True,
        postgresql_where=sa.text(
            "resume_sha256 IS NOT NULL"
        )
    )

    op.add_column(
        "resume_processing_jobs",
        sa.Column(
            "resume_sha256",
            sa.String(length=64),
            nullable=True
        )
    )
    op.create_check_constraint(
        (
            "ck_resume_processing_jobs_"
            "resume_sha256_format"
        ),
        "resume_processing_jobs",
        (
            "resume_sha256 IS NULL OR "
            "resume_sha256 ~ '^[0-9a-f]{64}$'"
        )
    )
    op.create_index(
        "ux_resume_processing_jobs_resume_sha256",
        "resume_processing_jobs",
        ["resume_sha256"],
        unique=True,
        postgresql_where=sa.text(
            "resume_sha256 IS NOT NULL"
        )
    )


def downgrade() -> None:

    op.drop_index(
        "ux_resume_processing_jobs_resume_sha256",
        table_name="resume_processing_jobs"
    )
    op.drop_constraint(
        (
            "ck_resume_processing_jobs_"
            "resume_sha256_format"
        ),
        "resume_processing_jobs",
        type_="check"
    )
    op.drop_column(
        "resume_processing_jobs",
        "resume_sha256"
    )

    op.drop_index(
        "ux_candidates_resume_sha256",
        table_name="candidates"
    )
    op.drop_constraint(
        "ck_candidates_resume_sha256_format",
        "candidates",
        type_="check"
    )
    op.drop_column(
        "candidates",
        "resume_sha256"
    )
