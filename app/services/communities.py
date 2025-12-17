from typing import Optional, List
from sqlalchemy import select, update, delete

from app.models.communities import CommunityModel
from app.schemes.communities import SCommunityAdd, SCommunityUpdate
from app.exceptions.communities import (
    CommunityNotFoundError,
    CommunityAlreadyExistsError
)


class CommunitiesService:
    def __init__(self, db):
        self.db = db  # DBManager instance

    async def create_community(self, community_data: SCommunityAdd) -> CommunityModel:
        """Создание нового сообщества"""
        # Проверка на уникальность названия
        existing_community = await self.db.communities.get_one_or_none(name=community_data.name)
        if existing_community:
            raise CommunityAlreadyExistsError
        
        community_data_dict = {
            'name': community_data.name,
            'description': community_data.description,
            'image': community_data.image,
            'posts_count': 0,
            'members_count': 0
        }
        
        new_community = await self.db.communities.add(community_data_dict)
        return new_community

    async def get_community(self, community_id: int) -> Optional[CommunityModel]:
        """Получение сообщества по ID"""
        return await self.db.communities.get(community_id)

    async def get_communities(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None
    ) -> List[CommunityModel]:
        """Получение списка сообществ"""
        filters = {}
        if search:
            # В репозитории уже есть метод поиска
            return await self.db.communities.search(search, skip, limit)
        else:
            return await self.db.communities.get_filtered(
                **filters,
                offset=skip,
                limit=limit
            )

    async def update_community(
        self,
        community_id: int,
        community_data: SCommunityUpdate
    ) -> None:
        """Обновление сообщества"""
        community = await self.get_community(community_id)
        if not community:
            raise CommunityNotFoundError
        
        # Подготовим данные для обновления
        update_data = {}
        if community_data.name is not None:
            update_data['name'] = community_data.name
        if community_data.description is not None:
            update_data['description'] = community_data.description
        if community_data.image is not None:
            update_data['image'] = community_data.image
        
        if update_data:
            # Проверяем уникальность имени, если оно изменяется
            if 'name' in update_data and update_data['name'] != community.name:
                existing_community = await self.db.communities.get_one_or_none(name=update_data['name'])
                if existing_community:
                    raise CommunityAlreadyExistsError
            
            await self.db.communities.edit(update_data, id=community_id)

    async def delete_community(self, community_id: int) -> None:
        """Удаление сообщества"""
        community = await self.get_community(community_id)
        if not community:
            raise CommunityNotFoundError
        
        await self.db.communities.delete(id=community_id)

    async def increment_posts_count(self, community_id: int) -> None:
        """Увеличение счетчика постов"""
        community = await self.db.communities.get(community_id)
        if community:
            update_data = {"posts_count": (community.posts_count or 0) + 1}
            await self.db.communities.edit(update_data, id=community_id)

    async def decrement_posts_count(self, community_id: int) -> None:
        """Уменьшение счетчика постов"""
        community = await self.db.communities.get(community_id)
        if community and community.posts_count > 0:
            update_data = {"posts_count": community.posts_count - 1}
            await self.db.communities.edit(update_data, id=community_id)

    async def increment_members_count(self, community_id: int) -> None:
        """Увеличение счетчика участников"""
        community = await self.db.communities.get(community_id)
        if community:
            update_data = {"members_count": (community.members_count or 0) + 1}
            await self.db.communities.edit(update_data, id=community_id)

    async def decrement_members_count(self, community_id: int) -> None:
        """Уменьшение счетчика участников"""
        community = await self.db.communities.get(community_id)
        if community and community.members_count > 0:
            update_data = {"members_count": community.members_count - 1}
            await self.db.communities.edit(update_data, id=community_id)

    async def join_community(self, community_id: int, user_id: int) -> None:
        """Присоединение пользователя к сообществу"""
        # Проверяем, что сообщество существует
        community = await self.get_community(community_id)
        if not community:
            raise CommunityNotFoundError
        
        # Проверяем, не состоит ли пользователь уже в сообществе
        existing_association = await self.db.user_communities.get_one_or_none(
            user_id=user_id,
            community_id=community_id
        )
        
        if existing_association:
            # Пользователь уже состоит в сообществе
            return
        
        # Создаем связь между пользователем и сообществом
        await self.db.user_communities.add({
            'user_id': user_id,
            'community_id': community_id
        })
        
        # Увеличиваем счетчик участников
        await self.increment_members_count(community_id)

    async def leave_community(self, community_id: int, user_id: int) -> None:
        """Выход пользователя из сообщества"""
        # Проверяем, что сообщество существует
        community = await self.get_community(community_id)
        if not community:
            raise CommunityNotFoundError
        
        # Находим связь между пользователем и сообществом
        association = await self.db.user_communities.get_one_or_none(
            user_id=user_id,
            community_id=community_id
        )
        
        if not association:
            # Пользователь не состоит в сообществе
            return
        
        # Удаляем связь
        await self.db.user_communities.delete(id=association.id)
        
        # Уменьшаем счетчик участников
        await self.decrement_members_count(community_id)