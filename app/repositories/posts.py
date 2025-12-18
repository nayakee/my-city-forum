from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func

from app.models.posts import PostModel
from app.repositories.base import BaseRepository
from app.schemes.posts import SPostGet


class PostsRepository(BaseRepository):
    """Репозиторий для работы с постами"""
    
    model = PostModel
    schema = SPostGet
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user(
        self, 
        user_id: int,
        skip: int = 0, 
        limit: int = 100
    ) -> List[PostModel]:
        """Получение постов пользователя"""
        query = (
            select(PostModel)
            .where(PostModel.user_id == user_id)
            .order_by(desc(PostModel.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_theme(
        self, 
        theme_id: int,
        skip: int = 0, 
        limit: int = 100
    ) -> List[PostModel]:
        """Получение постов по теме"""
        query = (
            select(PostModel)
            .where(PostModel.theme_id == theme_id)
            .order_by(desc(PostModel.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_community(
        self, 
        community_id: int,
        skip: int = 0, 
        limit: int = 100
    ) -> List[PostModel]:
        """Получение постов по сообществу"""
        query = (
            select(PostModel)
            .where(PostModel.community_id == community_id)
            .order_by(desc(PostModel.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def search(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[PostModel]:
        """Поиск постов по заголовку или содержанию"""
        from sqlalchemy import or_
        # Используем % для обозначения любого количества символов до и после search_term
        query = (
            select(PostModel)
            .where(
                or_(
                    PostModel.header.ilike(f"%{search_term}%"),
                    PostModel.body.ilike(f"%{search_term}%")
                )
            )
            .order_by(desc(PostModel.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_popular(
        self, 
        days: int = 7,
        skip: int = 0, 
        limit: int = 100
    ) -> List[PostModel]:
        """Получение популярных постов (по лайкам)"""
        query = (
            select(PostModel)
            .order_by(desc(PostModel.likes))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()