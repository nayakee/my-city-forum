from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.communities import CommunityModel
from app.repositories.base import BaseRepository


class CommunitiesRepository(BaseRepository[CommunityModel]):
    """Репозиторий для работы с сообществами"""
    
    def __init__(self, session: AsyncSession):
        self.model = CommunityModel
        self.session = session

    async def get_by_name(self, name: str) -> Optional[CommunityModel]:
        """Получение сообщества по имени"""
        query = select(CommunityModel).where(CommunityModel.name == name)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def search(
        self, 
        search_term: str,
        skip: int = 0, 
        limit: int = 100
    ) -> List[CommunityModel]:
        """Поиск сообществ по названию или описанию"""
        query = (
            select(CommunityModel)
            .where(
                CommunityModel.name.ilike(f"%{search_term}%") |
                CommunityModel.description.ilike(f"%{search_term}%")
            )
            .order_by(desc(CommunityModel.members_count))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_popular(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[CommunityModel]:
        """Получение популярных сообществ (по количеству участников)"""
        query = (
            select(CommunityModel)
            .order_by(desc(CommunityModel.members_count))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()