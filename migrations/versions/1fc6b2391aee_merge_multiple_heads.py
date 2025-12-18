"""merge multiple heads

Revision ID: 1fc6b2391aee
Revises: 5e8c3a0b7d5e, fcbc927b3e79
Create Date: 2025-12-17 22:44:04.660578

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1fc6b2391aee'
down_revision: Union[str, Sequence[str], None] = ('5e8c3a0b7d5e', 'fcbc927b3e79')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
