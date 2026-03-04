"""add title to memories

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-03-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "c4d5e6f7a8b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "memories",
        sa.Column("title", sa.String(100), nullable=False, server_default=""),
    )
    op.alter_column("memories", "title", server_default=None)


def downgrade() -> None:
    op.drop_column("memories", "title")
