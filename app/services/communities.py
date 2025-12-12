from typing import Optional, List
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.communities import CommunityModel
from app.schemes.communities import SCommunityAdd, SCommunityUpdate
from app.exceptions.communities import (
    CommunityNotFoundError,
    CommunityAlreadyExistsError
)


class CommunitiesService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_community(self, community_data: SCommunityAdd) -> CommunityModel:
        """Создание нового сообщества"""
        # Проверка на уникальность названия
        query = select(CommunityModel).where(CommunityModel.name == community_data.name)
        result = await self.db.execute(query)
        if result.scalar_one_or_none():
            raise CommunityAlreadyExistsError
        
        new_community = CommunityModel(
            name=community_data.name,
            description=community_data.description,
            posts_count=0,
            members_count=0
        )
        
        self.db.add(new_community)
        await self.db.commit()
        await self.db.refresh(new_community)
        return new_community

    async def get_community(self, community_id: int) -> Optional[CommunityModel]:
        """Получение сообщества по ID"""
        query = select(CommunityModel).where(CommunityModel.id == community_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_communities(
        self, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None
    ) -> List[CommunityModel]:
        """Получение списка сообществ"""
        query = select(CommunityModel)
        
        if search:
            query = query.where(
                CommunityModel.name.ilike(f"%{search}%") | 
                CommunityModel.description.ilike(f"%{search}%")
            )
        
        query = query.offset(skip).limit(limit).order_by(CommunityModel.members_count.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_community(
        self, 
        community_id: int, 
        community_data: SCommunityUpdate
    ) -> None:
        """Обновление сообщества"""
        community = await self.get_community(community_id)
        if not community:
            raise CommunityNotFoundError
        
        # Обновляем только переданные поля
        update_data = {}
        if community_data.name is not None:
            update_data['name'] = community_data.name
        if community_data.description is not None:
            update_data['description'] = community_data.description
        
        if update_data:
            # Проверяем уникальность имени, если оно изменяется
            if 'name' in update_data and update_data['name'] != community.name:
                check_query = select(CommunityModel).where(CommunityModel.name == update_data['name'])
                check_result = await self.db.execute(check_query)
                if check_result.scalar_one_or_none():
                    raise CommunityAlreadyExistsError
            
            query = (
                update(CommunityModel)
                .where(CommunityModel.id == community_id)
                .values(**update_data)
            )
            await self.db.execute(query)
            await self.db.commit()

    async def delete_community(self, community_id: int) -> None:
        """Удаление сообщества"""
        community = await self.get_community(community_id)
        if not community:
            raise CommunityNotFoundError
        
        query = delete(CommunityModel).where(CommunityModel.id == community_id)
        await self.db.execute(query)
        await self.db.commit()

    async def increment_posts_count(self, community_id: int) -> None:
        """Увеличение счетчика постов"""
        query = (
            update(CommunityModel)
            .where(CommunityModel.id == community_id)
            .values(posts_count=CommunityModel.posts_count + 1)
        )
        await self.db.execute(query)
        await self.db.commit()

    async def decrement_posts_count(self, community_id: int) -> None:
        """Уменьшение счетчика постов"""
        query = (
            update(CommunityModel)
            .where(CommunityModel.id == community_id)
            .values(posts_count=CommunityModel.posts_count - 1)
        )
        await self.db.execute(query)
        await self.db.commit()

    async def increment_members_count(self, community_id: int) -> None:
        """Увеличение счетчика участников"""
        query = (
            update(CommunityModel)
            .where(CommunityModel.id == community_id)
            .values(members_count=CommunityModel.members_count + 1)
        )
        await self.db.execute(query)
        await self.db.commit()

    async def decrement_members_count(self, community_id: int) -> None:
        """Уменьшение счетчика участников"""
        query = (
            update(CommunityModel)
            .where(CommunityModel.id == community_id)
            .values(members_count=CommunityModel.members_count - 1)
        )
        await self.db.execute(query)
        await self.db.commit()