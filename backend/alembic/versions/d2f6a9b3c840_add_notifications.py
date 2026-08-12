"""add in-app notifications

Revision ID: d2f6a9b3c840
Revises: c8f1d2e5a730
Create Date: 2026-08-13
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d2f6a9b3c840"
down_revision: Union[str, Sequence[str], None] = "c8f1d2e5a730"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.add_column(
        "resume_processing_jobs",
        sa.Column(
            "requested_by",
            sa.Integer(),
            nullable=True
        )
    )
    op.create_index(
        "ix_resume_processing_jobs_requested_by",
        "resume_processing_jobs",
        ["requested_by"],
        unique=False
    )
    op.create_foreign_key(
        "fk_resume_processing_jobs_requested_by_users",
        "resume_processing_jobs",
        "users",
        ["requested_by"],
        ["id"],
        ondelete="SET NULL"
    )

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("message", sa.String(length=500), nullable=False),
        sa.Column("candidate_id", sa.Integer(), nullable=True),
        sa.Column("event_key", sa.String(length=255), nullable=True),
        sa.Column(
            "is_read",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false()
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now()
        ),
        sa.CheckConstraint(
            "type IN ("
            "'RESUME_PROCESSING_COMPLETED', "
            "'RESUME_PROCESSING_FAILED', "
            "'CANDIDATE_STAGE_CHANGED'"
            ")",
            name="ck_notifications_type"
        ),
        sa.ForeignKeyConstraint(
            ["candidate_id"],
            ["candidates.id"],
            ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "event_key",
            name="uq_notifications_event_key"
        )
    )
    op.create_index(
        "ix_notifications_user_read_created",
        "notifications",
        ["user_id", "is_read", "created_at"],
        unique=False
    )


def downgrade() -> None:

    op.drop_index(
        "ix_notifications_user_read_created",
        table_name="notifications"
    )
    op.drop_table("notifications")
    op.drop_constraint(
        "fk_resume_processing_jobs_requested_by_users",
        "resume_processing_jobs",
        type_="foreignkey"
    )
    op.drop_index(
        "ix_resume_processing_jobs_requested_by",
        table_name="resume_processing_jobs"
    )
    op.drop_column(
        "resume_processing_jobs",
        "requested_by"
    )
