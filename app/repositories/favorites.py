from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.favorites import FavoritePostModel
from app.repositories.base import BaseRepository
from app.schemes.favorites import SFavoritePostGet


class FavoritesRepository(BaseRepository):
    """Репозиторий для работы с избранными постами"""
    
    model = FavoritePostModel
    schema = SFavoritePostGet
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_favorite(self, user_id: int, post_id: int) -> bool:
        """Добавляет пост в избранное для пользователя"""
        favorite = FavoritePostModel(user_id=user_id, post_id=post_id)
        self.session.add(favorite)
        try:
            await self.session.commit()
            return True
        except Exception:
            await self.session.rollback()
            return False

    async def remove_favorite(self, user_id: int, post_id: int) -> bool:
        """Удаляет пост из избранного пользователя"""
        stmt = delete(FavoritePostModel).where(
            FavoritePostModel.user_id == user_id,
            FavoritePostModel.post_id == post_id
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def is_favorite(self, user_id: int, post_id: int) -> bool:
        """Проверяет, находится ли пост в избранном у пользователя"""
        stmt = select(FavoritePostModel).where(
            FavoritePostModel.user_id == user_id,
            FavoritePostModel.post_id == post_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_user_favorites(self, user_id: int, skip: int = 0, limit: int = 100) -> List[FavoritePostModel]:
        """Получает список избранных постов пользователя"""
        stmt = (
            select(FavoritePostModel)
            .where(FavoritePostModel.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_favorite_post_ids(self, user_id: int) -> List[int]:
        """Получает список ID избранных постов пользователя"""
        stmt = select(FavoritePostModel.post_id).where(
            FavoritePostModel.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()