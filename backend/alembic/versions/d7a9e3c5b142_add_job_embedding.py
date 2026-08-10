"""add job embedding

Revision ID: d7a9e3c5b142
Revises: c4f8a2d1e730
Create Date: 2026-08-10
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


revision: str = "d7a9e3c5b142"
down_revision: Union[str, Sequence[str], None] = "c4f8a2d1e730"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.add_column(
        "jobs",
        sa.Column(
            "embedding",
            Vector(384),
            nullable=True
        )
    )


def downgrade() -> None:

    op.drop_column(
        "jobs",
        "embedding"
    )
