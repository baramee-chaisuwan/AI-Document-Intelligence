"""add users table

Revision ID: a8f4c2d9e731
Revises: d4433d68144d
Create Date: 2026-08-04
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a8f4c2d9e731"
down_revision: Union[
    str,
    Sequence[str],
    None
] = "d4433d68144d"
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

    op.create_table(
        "users",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            nullable=False
        ),
        sa.Column(
            "email",
            sa.String(length=320),
            nullable=False
        ),
        sa.Column(
            "full_name",
            sa.String(length=255),
            nullable=False
        ),
        sa.Column(
            "hashed_password",
            sa.String(length=255),
            nullable=False
        ),
        sa.Column(
            "role",
            sa.String(length=20),
            nullable=False,
            server_default="recruiter"
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true()
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now()
        ),
        sa.CheckConstraint(
            "role IN ('admin', 'recruiter')",
            name="ck_users_role"
        )
    )

    op.create_index(
        "ix_users_id",
        "users",
        ["id"],
        unique=False
    )

    op.create_index(
        "ix_users_email",
        "users",
        ["email"],
        unique=True
    )


def downgrade() -> None:

    op.drop_index(
        "ix_users_email",
        table_name="users"
    )

    op.drop_index(
        "ix_users_id",
        table_name="users"
    )

    op.drop_table(
        "users"
    )
