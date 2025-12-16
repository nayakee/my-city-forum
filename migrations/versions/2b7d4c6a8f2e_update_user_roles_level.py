"""update user roles level

Revision ID: 2b7d4c6a8f2e
Revises: ec32232aac4
Create Date: 2025-12-15 17:44:00.0000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2b7d4c6a8f2e'
down_revision: Union[str, None] = 'ec322322aac4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Обновляем уровень доступа для существующих ролей
    # ID=1 - пользователь (уровень 1)
    # ID=2 - модератор (уровень 2) 
    # ID=3 - администратор (уровень 3)
    conn = op.get_bind()
    
    # Обновляем уровень для существующих ролей
    conn.execute(sa.text("UPDATE roles SET level = 1 WHERE id = 1 AND name = 'user'"))
    conn.execute(sa.text("UPDATE roles SET level = 2 WHERE id = 2 AND name = 'moderator'"))
    conn.execute(sa.text("UPDATE roles SET level = 3 WHERE id = 3 AND name = 'admin'"))
    
    # Если таких ролей нет, создаем их
    conn.execute(sa.text("""
        INSERT OR IGNORE INTO roles (id, name, level) 
        VALUES 
            (1, 'user', 1),
            (2, 'moderator', 2),
            (3, 'admin', 3)
    """))
    
    # Обновляем role_id у существующих пользователей, у которых role_id NULL или несуществующий
    # Устанавливаем по умолчанию role_id = 1 (пользовательская роль)
    conn.execute(sa.text("""
        UPDATE users 
        SET role_id = 1 
        WHERE role_id IS NULL OR role_id NOT IN (SELECT id FROM roles)
    """))


def downgrade() -> None:
    # Возвращаем уровни доступа к NULL
    conn = op.get_bind()
    conn.execute(sa.text("UPDATE roles SET level = NULL WHERE id IN (1, 2, 3)"))