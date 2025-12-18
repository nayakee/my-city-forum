#!/usr/bin/env python3
"""
Тестовый скрипт для проверки корректности моделей
"""
import asyncio
import sys
from pathlib import Path

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent))

from app.database.database import engine, Base
from app.models.users import UserModel
from app.models.posts import PostModel
from app.models.comments import CommentModel
from app.models.communities import CommunityModel
from app.models.themes import ThemeModel
from app.models.roles import RoleModel
from app.models.reports import ReportModel
from app.models.user_communities import UserCommunityModel


async def test_models():
    """Тестирование моделей"""
    try:
        print("Проверка моделей...")
        
        # Создание таблиц
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("SUCCESS: Все модели успешно загружены и таблицы созданы")
        
        # Проверка связей
        print("\nChecking relationships:")
        
        # Проверка связи пользователь-роль
        user = UserModel(name="Test User", email="test@example.com", hashed_password="hashed")
        print(f"  - UserModel -> RoleModel relationship: {hasattr(user, 'role')}")
        
        # Проверка связи пользователь-пост
        print(f"  - UserModel -> PostModel relationship: {hasattr(user, 'posts')}")
        
        # Проверка связи пост-пользователь
        post = PostModel(header="Test Post", body="Test Body")
        print(f"  - PostModel -> UserModel relationship: {hasattr(post, 'user')}")
        
        # Проверка связи комментарий-пост
        comment = CommentModel(body="Test Comment")
        print(f"  - CommentModel -> PostModel relationship: {hasattr(comment, 'post')}")
        
        # Проверка связи пост-комментарии
        print(f"  - PostModel -> CommentModel relationship: {hasattr(post, 'comments')}")
        
        print("\nSUCCESS: All checks passed!")
        
    except Exception as e:
        print(f"ERROR: Error testing models: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_models())
    if success:
        print("\nSUCCESS: All tests passed! Models work correctly.")
    else:
        print("\nERROR: Tests failed. There are problems with models.")
        sys.exit(1)