"""Add post_reactions table

Revision ID: 5e8c3a0b7d5e
Revises: 46209a0a1870
Create Date: 2025-12-17 18:41:0.00000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5e8c3a0b7d5e'
down_revision: Union[str, Sequence[str], None] = '46209a0a1870'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create post_reactions table
    op.create_table('post_reactions',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.Column('reaction_type', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'post_id')
    )


def downgrade() -> None:
    # Drop post_reactions table
    op.drop_table('post_reactions')