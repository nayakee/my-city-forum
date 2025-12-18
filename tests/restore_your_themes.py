#!/usr/bin/env python3
"""
Скрипт для восстановления ваших конкретных тем: "новости", "недвижимость", "работа"
"""

import asyncio
import sys
from pathlib import Path

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent))

from app.database.database import create_tables
from app.database.db_manager import DBManager
from app.services.themes import ThemeService
from app.schemes.themes import SThemeCreate


async def restore_your_themes():
    """Восстановление ваших тем: новости, недвижимость, работа"""
    print("Начинаем восстановление ваших тем: новости, недвижимость, работа...")
    
    # Создаем таблицы, если они не существуют
    await create_tables()
    
    async with DBManager() as db_manager:
        theme_service = ThemeService(db_manager)
        
        # Ваши темы
        your_themes = ["новости", "недвижимость", "работа"]
        
        created_count = 0
        for theme_name in your_themes:
            try:
                # Проверяем, существует ли тема уже
                existing_theme = await db_manager.themes.get_by_name(theme_name)
                if existing_theme:
                    print(f"✓ Тема '{theme_name}' уже существует (ID: {existing_theme.id})")
                else:
                    theme_data = SThemeCreate(name=theme_name)
                    created_theme = await theme_service.create_theme(theme_data)
                    print(f"✓ Создана тема: {created_theme.name} (ID: {created_theme.id})")
                    created_count += 1
            except Exception as e:
                print(f"✗ Ошибка при создании темы '{theme_name}': {e}")
        
        print(f"\nГотово! Создано новых тем: {created_count}")
        
        # Показываем все темы после восстановления
        all_themes = await db_manager.themes.get_all()
        print(f"Всего тем в базе данных: {len(all_themes)}")
        
        # Сначала показываем ваши темы
        print("\nВаши темы:")
        for theme_name in your_themes:
            theme = await db_manager.themes.get_by_name(theme_name)
            if theme:
                print(f"  - ID: {theme.id}, Название: {theme.name}, Постов: {theme.posts_count}")
        
        print("\nВсе темы в системе:")
        for theme in all_themes:
            status = "ВАША" if theme.name in your_themes else "СТАНДАРТНАЯ"
            print(f" - ID: {theme.id}, Название: {theme.name}, Постов: {theme.posts_count} [{status}]")


if __name__ == "__main__":
    asyncio.run(restore_your_themes())