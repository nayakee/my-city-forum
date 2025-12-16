"""add level field to roles

Revision ID: 07453c7f0d1c
Revises: 6755a05b4dbd
Create Date: 2025-12-15 17:13:25.123456

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '07453c7f0d1c'
down_revision: Union[str, None] = '6755a05b4dbd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем колонку level в таблицу roles
    op.add_column('roles', sa.Column('level', sa.Integer(), nullable=False, default=1))
    
    # Создаем роли по умолчанию: пользователь, модератор, администратор
    # Сначала добавим администратора (если его нет)
    conn = op.get_bind()
    conn.execute(sa.text("INSERT OR IGNORE INTO roles (id, name, level) VALUES (1, 'user', 1)"))
    conn.execute(sa.text("INSERT OR IGNORE INTO roles (id, name, level) VALUES (2, 'moderator', 2)"))
    conn.execute(sa.text("INSERT OR IGNORE INTO roles (id, name, level) VALUES (3, 'admin', 3)"))


def downgrade() -> None:
    # Удаляем колонку level из таблицы roles
    op.drop_column('roles', 'level')