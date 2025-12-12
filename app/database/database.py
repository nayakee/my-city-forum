from datetime import datetime
from typing import TYPE_CHECKING, AsyncGenerator
from pathlib import Path

from sqlalchemy import NullPool, func, text
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
    AsyncSession
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.config import settings

BASE_DIR = Path(__file__).parent.parent
DATABASE_URL = f"sqlite+aiosqlite:///{BASE_DIR}/forum.db"

engine = create_async_engine(settings.get_db_url)

engine_null_pool = create_async_engine(settings.get_db_url, poolclass=NullPool)


async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)
async_session_maker_null_pool = async_sessionmaker(
    bind=engine_null_pool, expire_on_commit=False
)


class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency для получения асинхронной сессии"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    """Создание всех таблиц в базе данных"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Таблицы базы данных созданы")


async def drop_tables():
    """Удаление всех таблиц из базы данных (для тестов)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("🗑️  Таблицы базы данных удалены")


def create_sync_engine():
    """Создание синхронного движка для Alembic миграций"""
    from sqlalchemy import create_engine
    sync_database_url = f"sqlite:///{BASE_DIR}/forum.db"
    return create_engine(sync_database_url, echo=True)
