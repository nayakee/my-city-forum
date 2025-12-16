#!/usr/bin/env python3
"""
Тестовый скрипт для проверки API тем
"""
import asyncio
import sys
from pathlib import Path

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent))

import httpx
from app.database.database import DATABASE_URL


async def test_themes_api():
    """
    Тестирует API для получения тем
    """
    print("Тестируем API тем...")
    
    # Используем httpx для асинхронного запроса к API
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
        try:
            response = await client.get("/themes")
            print(f"Статус ответа: {response.status_code}")
            
            if response.status_code == 200:
                themes = response.json()
                print(f"Получено тем: {len(themes)}")
                print("Темы:")
                for theme in themes:
                    print(f"  - ID: {theme['id']}, Название: '{theme['name']}', Постов: {theme['posts_count']}")
            else:
                print(f"Ошибка: {response.status_code}")
                print(f"Ответ: {response.text}")
                
        except httpx.ConnectError:
            print("Ошибка подключения. Убедитесь, что сервер запущен на http://127.0.0.1:8000")
        except Exception as e:
            print(f"Произошла ошибка: {e}")


async def test_themes_db():
    """
    Тестирует напрямую базу данных
    """
    print("\nПроверяем темы в базе данных...")
    
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    
    # Создаем синхронный движок
    sync_engine = create_engine(DATABASE_URL.replace("+aiosqlite", ""))
    SessionLocal = sessionmaker(bind=sync_engine)
    
    with SessionLocal() as session:
        result = session.execute(text("SELECT id, name, posts_count FROM themes"))
        themes = result.fetchall()
        
        print(f"Найдено {len(themes)} тем в базе данных:")
        for theme in themes:
            print(f"  - ID: {theme.id}, Название: '{theme.name}', Постов: {theme.posts_count}")


if __name__ == "__main__":
    print("Запускаем тесты...")
    asyncio.run(test_themes_db())
    print("\nДля проверки API запустите сервер командой: python -m uvicorn main:app --reload")
    print("Затем запустите этот скрипт снова для проверки API.")