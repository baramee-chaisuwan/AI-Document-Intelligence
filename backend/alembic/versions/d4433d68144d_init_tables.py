"""init tables

Revision ID: d4433d68144d
Revises:
Create Date: 2026-06-28 16:51:17.308796
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d4433d68144d"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        "candidates",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            nullable=False
        ),

        sa.Column(
            "name",
            sa.String(),
            nullable=False
        ),

        sa.Column(
            "summary",
            sa.Text(),
            nullable=False
        ),

        sa.Column(
            "candidate_level",
            sa.String(),
            nullable=False
        ),

        sa.Column(
            "skill_score",
            sa.Integer(),
            nullable=False,
            server_default="0"
        ),

        sa.Column(
            "rule_score",
            sa.Integer(),
            nullable=False,
            server_default="0"
        ),

        sa.Column(
            "ai_score",
            sa.Integer(),
            nullable=False,
            server_default="0"
        ),

        sa.Column(
            "ai_status",
            sa.String(),
            nullable=False,
            server_default="success"
        ),

        sa.Column(
            "score_breakdown",
            sa.JSON(),
            nullable=True
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now()
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True
        ),
    )

    op.create_index(
        "ix_candidates_id",
        "candidates",
        ["id"],
        unique=False
    )


def downgrade() -> None:

    op.drop_index(
        "ix_candidates_id",
        table_name="candidates"
    )

    op.drop_table(
        "candidates"
    )