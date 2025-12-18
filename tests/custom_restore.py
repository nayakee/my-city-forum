#!/usr/bin/env python3
"""
Скрипт для восстановления конкретных тем, которые у вас были
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


async def restore_custom_themes(theme_names):
    """Восстановление пользовательских тем"""
    print("Начинаем восстановление ваших тем...")
    
    # Создаем таблицы, если они не существуют
    await create_tables()
    
    async with DBManager() as db_manager:
        theme_service = ThemeService(db_manager)
        
        # Удаляем существующие темы (если нужно заменить)
        existing_themes = await db_manager.themes.get_all()
        if existing_themes:
            print(f"Найдено {len(existing_themes)} существующих тем")
            # Закомментируйте следующий блок, если не хотите удалять существующие темы
            # for theme in existing_themes:
            #     await theme_service.delete_theme(theme.id)
            # print("Существующие темы удалены")
        
        # Создаем ваши 3 темы
        for theme_name in theme_names:
            try:
                # Проверяем, существует ли тема уже
                existing_theme = await db_manager.themes.get_by_name(theme_name)
                if existing_theme:
                    print(f"Тема '{theme_name}' уже существует (ID: {existing_theme.id})")
                    continue
                
                theme_data = SThemeCreate(name=theme_name)
                created_theme = await theme_service.create_theme(theme_data)
                print(f"Создана тема: {created_theme.name} (ID: {created_theme.id})")
            except Exception as e:
                print(f"Ошибка при создании темы '{theme_name}': {e}")
        
        # Показываем все темы после восстановления
        all_themes = await db_manager.themes.get_all()
        print(f"\nВсего тем после восстановления: {len(all_themes)}")
        for theme in all_themes:
            print(f"  - ID: {theme.id}, Название: {theme.name}, Постов: {theme.posts_count}")


def main():
    print("Скрипт восстановления ваших тем")
    print("Укажите названия ваших 3 тем")
    
    # Можно изменить этот список на ваши реальные темы
    custom_themes = [
        input("Введите название первой темы: "),
        input("Введите название второй темы: "), 
        input("Введите название третьей темы: ")
    ]
    
    # Убираем пустые названия
    custom_themes = [theme for theme in custom_themes if theme.strip()]
    
    if not custom_themes:
        print("Не введено ни одной темы. Используем примеры:")
        custom_themes = ["Общие вопросы", "Политика", "Экономика"]
    
    print(f"Будет восстановлено {len(custom_themes)} тем: {custom_themes}")
    
    confirm = input("Продолжить? (y/n): ")
    if confirm.lower() in ['y', 'yes', 'да', 'д']:
        asyncio.run(restore_custom_themes(custom_themes))
    else:
        print("Операция отменена")


if __name__ == "__main__":
    main()