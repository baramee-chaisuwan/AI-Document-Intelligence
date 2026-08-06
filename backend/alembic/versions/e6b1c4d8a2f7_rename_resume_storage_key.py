"""rename resume storage key

Revision ID: e6b1c4d8a2f7
Revises: c3e7a91b4f20
Create Date: 2026-08-06
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e6b1c4d8a2f7"
down_revision: Union[
    str,
    Sequence[str],
    None
] = "c3e7a91b4f20"
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

    op.alter_column(
        "candidates",
        "resume_s3_key",
        new_column_name="resume_storage_key",
        existing_type=sa.String(length=1024),
        existing_nullable=True
    )


def downgrade() -> None:

    op.alter_column(
        "candidates",
        "resume_storage_key",
        new_column_name="resume_s3_key",
        existing_type=sa.String(length=1024),
        existing_nullable=True
    )
