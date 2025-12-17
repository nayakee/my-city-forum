"""Add user_communities table

Revision ID: 46209a0a1870
Revises: 2b7d4c6a8f2e
Create Date: 2025-12-17 14:54:45.949693

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '46209a0a1870'
down_revision: Union[str, Sequence[str], None] = '2b7d4c6a8f2e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Сохраняем данные из существующей таблицы
    connection = op.get_bind()
    
    # Проверяем, существует ли старая таблица
    result = connection.execute(sa.text(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='user_communities';"
    ))
    table_exists = result.fetchone() is not None
    
    if table_exists:
        # Переименовываем старую таблицу
        op.rename_table('user_communities', 'user_communities_old')
    
    # Создаем новую таблицу с правильной структурой
    op.create_table('user_communities',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('community_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['community_id'], ['communities.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    
    # Копируем данные из старой таблицы в новую
    if table_exists:
        connection.execute(sa.text(
            "INSERT INTO user_communities (user_id, community_id, created_at, updated_at) "
            "SELECT user_id, community_id, created_at, updated_at FROM user_communities_old;"
        ))
        
        # Удаляем старую таблицу
        op.drop_table('user_communities_old')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('user_communities')
