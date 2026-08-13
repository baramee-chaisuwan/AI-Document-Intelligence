"""add user profile image metadata

Revision ID: e4a7c1d9b250
Revises: d2f6a9b3c840
Create Date: 2026-08-14
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e4a7c1d9b250"
down_revision: Union[str, Sequence[str], None] = "d2f6a9b3c840"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "profile_image_key",
            sa.String(length=1024),
            nullable=True
        )
    )


def downgrade() -> None:
    op.drop_column("users", "profile_image_key")
