"""add blocked role

Revision ID: 4670640018b9
Revises: 87a0de95d8e3
Create Date: 2025-12-18 23:59:30.134025

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4670640018b9'
down_revision: Union[str, Sequence[str], None] = '87a0de95d8e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create blocked role with level 0
    op.execute("INSERT OR IGNORE INTO roles (id, name, level) VALUES (4, 'blocked', 0)")


def downgrade() -> None:
    """Downgrade schema."""
    # Remove blocked role
    op.execute("DELETE FROM roles WHERE name = 'blocked'")
