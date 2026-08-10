"""add password reset tokens

Revision ID: b9d6f2a7c410
Revises: f7c2a9e4b610
Create Date: 2026-08-10
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b9d6f2a7c410"
down_revision: Union[str, Sequence[str], None] = "f7c2a9e4b610"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.add_column(
        "users",
        sa.Column(
            "token_version",
            sa.Integer(),
            nullable=False,
            server_default="0"
        )
    )

    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "otp_hash",
            sa.String(length=255),
            nullable=False
        ),
        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now()
        ),
        sa.Column(
            "verified_at",
            sa.DateTime(timezone=True),
            nullable=True
        ),
        sa.Column(
            "consumed_at",
            sa.DateTime(timezone=True),
            nullable=True
        ),
        sa.Column(
            "invalidated_at",
            sa.DateTime(timezone=True),
            nullable=True
        ),
        sa.Column(
            "failed_attempts",
            sa.Integer(),
            nullable=False,
            server_default="0"
        ),
        sa.CheckConstraint(
            "failed_attempts >= 0",
            name="ck_password_reset_tokens_failed_attempts"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_password_reset_tokens_user_id_users",
            ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name="pk_password_reset_tokens"
        )
    )

    op.create_index(
        "ix_password_reset_tokens_user_id",
        "password_reset_tokens",
        ["user_id"],
        unique=False
    )
    op.create_index(
        "ix_password_reset_tokens_expires_at",
        "password_reset_tokens",
        ["expires_at"],
        unique=False
    )
    op.create_index(
        "ix_password_reset_tokens_user_created",
        "password_reset_tokens",
        ["user_id", "created_at"],
        unique=False
    )


def downgrade() -> None:

    op.drop_index(
        "ix_password_reset_tokens_user_created",
        table_name="password_reset_tokens"
    )
    op.drop_index(
        "ix_password_reset_tokens_expires_at",
        table_name="password_reset_tokens"
    )
    op.drop_index(
        "ix_password_reset_tokens_user_id",
        table_name="password_reset_tokens"
    )
    op.drop_table("password_reset_tokens")
    op.drop_column("users", "token_version")
