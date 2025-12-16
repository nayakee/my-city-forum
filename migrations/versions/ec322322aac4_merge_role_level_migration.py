"""Merge role level migration

Revision ID: ec322322aac4
Revises: 7b1059511710, 07453c7f0d1c
Create Date: 2025-12-15 20:16:28.096044

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ec322322aac4'
down_revision: Union[str, Sequence[str], None] = ('7b1059511710', '07453c7f0d1c')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
