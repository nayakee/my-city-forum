import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from app.database import engine, sync_engine
from sqlalchemy import text, inspect


async def check_async_connection():
    """Проверка асинхронного подключения"""
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            data = result.scalar()
            print(f"✅ Асинхронное подключение работает: {data}")
    except Exception as e:
        print(f"❌ Ошибка асинхронного подключения: {e}")


def check_sync_connection():
    """Проверка синхронного подключения"""
    try:
        with sync_engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            data = result.scalar()
            print(f"✅ Синхронное подключение работает: {data}")
            
            # Проверяем таблицы через inspect
            inspector = inspect(sync_engine)
            tables = inspector.get_table_names()
            print(f"✅ Найдено таблиц: {len(tables)}")
            for table in tables:
                print(f"   - {table}")
    except Exception as e:
        print(f"❌ Ошибка синхронного подключения: {e}")


def main():
    print("🔍 Проверка базы данных SQLite")
    print("=" * 40)
    
    # Проверяем синхронное подключение
    check_sync_connection()
    
    # Проверяем асинхронное подключение
    asyncio.run(check_async_connection())


if __name__ == "__main__":
    main()