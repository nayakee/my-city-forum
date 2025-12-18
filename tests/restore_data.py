#!/usr/bin/env python3
"""
Скрипт для восстановления данных в базе данных
Восстанавливает пользователей и темы, если они были потеряны
"""

import asyncio
import sys
from pathlib import Path

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent))

from app.database.database import create_tables
from app.database.db_manager import DBManager
from app.models.users import UserModel
from app.models.themes import ThemeModel
from app.models.roles import RoleModel
from app.schemes.themes import SThemeCreate
from app.services.themes import ThemeService
from app.config import settings


async def init_default_themes(db_manager: DBManager):
    """Инициализация стандартных тем"""
    print("Инициализация тем...")
    
    theme_service = ThemeService(db_manager)
    
    # Проверяем, есть ли уже темы
    existing_themes = await db_manager.themes.get_all()
    if existing_themes:
        print(f"Найдено {len(existing_themes)} тем, пропускаем создание новых")
        return
    
    # Дефолтные темы для форума
    default_themes = [
        "Общие вопросы",
        "Политика",
        "Экономика",
        "Наука и технологии",
        "Культура",
        "Спорт",
        "Здоровье",
        "Образование",
        "Путешествия",
        "Еда и кулинария"
    ]
    
    for theme_name in default_themes:
        try:
            theme_data = SThemeCreate(name=theme_name)
            await theme_service.create_theme(theme_data)
            print(f"Создана тема: {theme_name}")
        except Exception as e:
            print(f"Ошибка при создании темы '{theme_name}': {e}")
    
    print("Создание тем завершено")


async def init_default_roles(db_manager: DBManager):
    """Инициализация стандартных ролей"""
    print("Инициализация ролей...")
    
    roles = await db_manager.roles.get_all()
    if roles:
        print(f"Найдено {len(roles)} ролей, пропускаем создание новых")
        return
    
    # Создаем базовые роли
    from app.schemes.roles import SRoleAdd
    
    admin_role = SRoleAdd(
        name="Администратор",
        level=10
    )
    moderator_role = SRoleAdd(
        name="Модератор",
        level=50
    )
    user_role = SRoleAdd(
        name="Пользователь",
        level=10
    )
    
    await db_manager.roles.add(admin_role.model_dump())
    await db_manager.roles.add(moderator_role.model_dump())
    await db_manager.roles.add(user_role.model_dump())
    
    print("Создание ролей завершено")


async def restore_data():
    """Основная функция восстановления данных"""
    print("Начинаем восстановление данных...")
    
    # Создаем таблицы, если они не существуют
    await create_tables()
    
    # Используем DBManager как контекстный менеджер
    async with DBManager() as db_manager:
        # Инициализируем роли
        await init_default_roles(db_manager)
        
        # Инициализируем темы
        await init_default_themes(db_manager)
        
        # Проверяем, есть ли пользователи
        users = await db_manager.users.get_all()
        print(f"Найдено {len(users)} пользователей")
        
        for user in users:
            print(f"  - ID: {user.id}, Имя: {user.name}, Email: {user.email}")
        
        # Подсчитываем количество тем
        themes = await db_manager.themes.get_all()
        print(f"Найдено {len(themes)} тем")
        
        for theme in themes:
            print(f"  - ID: {theme.id}, Название: {theme.name}, Постов: {theme.posts_count}")
        
        print("Восстановление данных завершено!")


if __name__ == "__main__":
    asyncio.run(restore_data())