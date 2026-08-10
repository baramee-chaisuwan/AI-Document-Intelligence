"""add jobs table

Revision ID: c4f8a2d1e730
Revises: b9d6f2a7c410
Create Date: 2026-08-10
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c4f8a2d1e730"
down_revision: Union[str, Sequence[str], None] = "b9d6f2a7c410"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        "jobs",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "title",
            sa.String(length=255),
            nullable=False
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=False
        ),
        sa.Column(
            "extracted_requirements",
            sa.JSON(),
            nullable=False
        ),
        sa.Column(
            "created_by",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now()
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
            name="fk_jobs_created_by_users",
            ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name="pk_jobs"
        )
    )

    op.create_index(
        "ix_jobs_created_by",
        "jobs",
        ["created_by"],
        unique=False
    )


def downgrade() -> None:

    op.drop_index(
        "ix_jobs_created_by",
        table_name="jobs"
    )
    op.drop_table("jobs")
