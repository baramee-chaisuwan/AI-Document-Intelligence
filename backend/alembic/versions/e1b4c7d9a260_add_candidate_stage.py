"""add candidate stage

Revision ID: e1b4c7d9a260
Revises: d7a9e3c5b142
Create Date: 2026-08-11
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e1b4c7d9a260"
down_revision: Union[str, Sequence[str], None] = "d7a9e3c5b142"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.add_column(
        "candidates",
        sa.Column(
            "candidate_stage",
            sa.String(length=20),
            server_default=sa.text("'APPLIED'"),
            nullable=True
        )
    )

    op.execute(
        sa.text(
            "UPDATE candidates "
            "SET candidate_stage = 'APPLIED' "
            "WHERE candidate_stage IS NULL"
        )
    )

    op.alter_column(
        "candidates",
        "candidate_stage",
        existing_type=sa.String(length=20),
        nullable=False,
        existing_server_default=sa.text("'APPLIED'")
    )

    op.create_check_constraint(
        "ck_candidates_candidate_stage",
        "candidates",
        (
            "candidate_stage IN "
            "('APPLIED', 'SCREENING', "
            "'INTERVIEW', 'OFFER', 'REJECTED')"
        )
    )


def downgrade() -> None:

    op.drop_constraint(
        "ck_candidates_candidate_stage",
        "candidates",
        type_="check"
    )

    op.drop_column(
        "candidates",
        "candidate_stage"
    )
