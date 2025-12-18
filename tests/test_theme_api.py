#!/usr/bin/env python3
"""
Простой тест API тем
"""
import asyncio
import sys
from pathlib import Path

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent))

from app.database.database import DATABASE_URL
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.repositories.themes import ThemesRepository
from app.database.db_manager import DBManager


async def test_theme_api_logic():
    """
    Тестируем логику API тем
    """
    print("=== Тестируем логику API тем ===")
    
    # Создаем асинхронный движок и сессию
    async with DBManager() as db_manager:
        themes_repo = ThemesRepository(db_manager.session)
        
        # Получаем все темы
        themes = await themes_repo.get_all()
        
        print(f"Найдено тем: {len(themes)}")
        for theme in themes:
            print(f"  - ID: {theme.id}, Название: '{theme.name}', Постов: {theme.posts_count}")
        
        # Проверим, что данные можно преобразовать в словарь
        print("\n=== Преобразование в словарь ===")
        for theme in themes:
            theme_dict = {
                "id": theme.id,
                "name": theme.name,
                "posts_count": theme.posts_count or 0,
                "created_at": getattr(theme, 'created_at', None),
                "updated_at": getattr(theme, 'updated_at', None)
            }
            print(f"  Словарь темы: {theme_dict}")
        
        return themes


if __name__ == "__main__":
    asyncio.run(test_theme_api_logic())