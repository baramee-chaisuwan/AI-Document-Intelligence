"""add resume processing jobs

Revision ID: f4a6c8e2d190
Revises: e1b4c7d9a260
Create Date: 2026-08-11
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f4a6c8e2d190"
down_revision: Union[str, Sequence[str], None] = "e1b4c7d9a260"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        "resume_processing_jobs",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "candidate_id",
            sa.Integer(),
            nullable=True
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'PENDING'"),
            nullable=False
        ),
        sa.Column(
            "error_message",
            sa.Text(),
            nullable=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False
        ),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=True
        ),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=True
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False
        ),
        sa.CheckConstraint(
            (
                "status IN "
                "('PENDING', 'PROCESSING', "
                "'COMPLETED', 'FAILED')"
            ),
            name=(
                "ck_resume_processing_jobs_status"
            )
        ),
        sa.ForeignKeyConstraint(
            ["candidate_id"],
            ["candidates.id"],
            ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id")
    )

    op.create_index(
        "ix_resume_processing_jobs_candidate_id",
        "resume_processing_jobs",
        ["candidate_id"],
        unique=False
    )

    op.create_index(
        "ix_resume_processing_jobs_status_created_at",
        "resume_processing_jobs",
        ["status", "created_at"],
        unique=False
    )


def downgrade() -> None:

    op.drop_index(
        "ix_resume_processing_jobs_status_created_at",
        table_name="resume_processing_jobs"
    )

    op.drop_index(
        "ix_resume_processing_jobs_candidate_id",
        table_name="resume_processing_jobs"
    )

    op.drop_table(
        "resume_processing_jobs"
    )
