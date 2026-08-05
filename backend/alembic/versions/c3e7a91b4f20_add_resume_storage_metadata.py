"""add resume storage metadata

Revision ID: c3e7a91b4f20
Revises: a8f4c2d9e731
Create Date: 2026-08-05
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c3e7a91b4f20"
down_revision: Union[
    str,
    Sequence[str],
    None
] = "a8f4c2d9e731"
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

    op.add_column(
        "candidates",
        sa.Column(
            "resume_s3_key",
            sa.String(length=1024),
            nullable=True
        )
    )

    op.add_column(
        "candidates",
        sa.Column(
            "resume_filename",
            sa.String(length=255),
            nullable=True
        )
    )


def downgrade() -> None:

    op.drop_column(
        "candidates",
        "resume_filename"
    )

    op.drop_column(
        "candidates",
        "resume_s3_key"
    )
