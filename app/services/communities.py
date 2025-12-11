from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.communities import CommunityModel
from app.models.user_communities import UserCommunityModel
from app.models.users import UserModel
from app.exceptions.communities import (
    CommunityNotFoundError,
    CommunityAlreadyExistsError,
    UserAlreadyInCommunityError,
    UserNotInCommunityError,
)


class CommunitiesService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def _check_admin_permission(self, user_id: int) -> bool:
        """
        Проверяет, является ли пользователь администратором.
        TODO: Реализовать проверку ролей когда будет готова база.
        """
        # Временная заглушка для тестирования
        # В реальном приложении проверяй user.role.name == "admin"
        return True
    
    async def get_communities(
        self, 
        search: Optional[str] = None,
        skip: int = 0, 
        limit: int = 20
    ) -> List[CommunityModel]:
        """
        Получение списка сообществ с поиском.
        """
        stmt = select(CommunityModel)
        
        if search:
            stmt = stmt.where(
                CommunityModel.name.ilike(f"%{search}%") | 
                CommunityModel.description.ilike(f"%{search}%")
            )
        
        stmt = stmt.order_by(CommunityModel.members_count.desc())
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_community_by_id(self, community_id: int) -> Optional[CommunityModel]:
        """
        Получение сообщества по ID.
        """
        stmt = select(CommunityModel).where(CommunityModel.id == community_id)
        result = await self.db.execute(stmt)
        community = result.scalar_one_or_none()
        
        if not community:
            raise CommunityNotFoundError()
        
        return community
    
    async def join_community(self, user_id: int, community_id: int) -> None:
        """
        Присоединение пользователя к сообществу.
        """
        community = await self.get_community_by_id(community_id)
        
        # Проверяем, не состоит ли уже пользователь в сообществе
        stmt = select(UserCommunityModel).where(
            and_(
                UserCommunityModel.user_id == user_id,
                UserCommunityModel.community_id == community_id
            )
        )
        result = await self.db.execute(stmt)
        existing_membership = result.scalar_one_or_none()
        
        if existing_membership:
            raise UserAlreadyInCommunityError()
        
        # Добавляем пользователя в сообщество
        user_community = UserCommunityModel(
            user_id=user_id,
            community_id=community_id,
            joined_at=datetime.now()
        )
        
        self.db.add(user_community)
        community.members_count += 1
        await self.db.commit()
    
    async def leave_community(self, user_id: int, community_id: int) -> None:
        """
        Выход пользователя из сообщества.
        """
        community = await self.get_community_by_id(community_id)
        
        # Проверяем, состоит ли пользователь в сообществе
        stmt = select(UserCommunityModel).where(
            and_(
                UserCommunityModel.user_id == user_id,
                UserCommunityModel.community_id == community_id
            )
        )
        result = await self.db.execute(stmt)
        membership = result.scalar_one_or_none()
        
        if not membership:
            raise UserNotInCommunityError()
        
        # Удаляем пользователя из сообщества
        await self.db.delete(membership)
        community.members_count -= 1
        await self.db.commit()
    
    async def get_user_communities(self, user_id: int) -> List[dict]:
        """
        Получение сообществ, в которых состоит пользователь.
        """
        stmt = select(
            CommunityModel,
            UserCommunityModel.joined_at
        ).join(
            UserCommunityModel,
            CommunityModel.id == UserCommunityModel.community_id
        ).where(
            UserCommunityModel.user_id == user_id
        )
        
        result = await self.db.execute(stmt)
        return result.all()
    
    async def get_community_members(
        self, 
        community_id: int, 
        skip: int = 0, 
        limit: int = 50
    ) -> List[dict]:
        """
        Получение участников сообщества.
        """
        await self.get_community_by_id(community_id)
        
        stmt = select(
            UserCommunityModel,
            UserModel.username
        ).join(
            UserModel,
            UserCommunityModel.user_id == UserModel.id
        ).where(
            UserCommunityModel.community_id == community_id
        ).order_by(UserCommunityModel.joined_at.desc())
        stmt = stmt.offset(skip).limit(limit)
        
        result = await self.db.execute(stmt)
        return result.all()
    
    async def is_user_in_community(self, user_id: int, community_id: int) -> bool:
        """
        Проверяет, состоит ли пользователь в сообществе.
        """
        stmt = select(UserCommunityModel).where(
            and_(
                UserCommunityModel.user_id == user_id,
                UserCommunityModel.community_id == community_id
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    # ============ АДМИНСКИЕ МЕТОДЫ ============
    
    async def create_community(self, user_id: int, name: str, description: str) -> CommunityModel:
        """
        Создание нового сообщества (только для администраторов).
        """
        
        # Проверяем, существует ли уже сообщество с таким именем
        stmt = select(CommunityModel).where(CommunityModel.name == name)
        result = await self.db.execute(stmt)
        existing_community = result.scalar_one_or_none()
        
        if existing_community:
            raise CommunityAlreadyExistsError()
        
        # Создаем новое сообщество
        community = CommunityModel(
            name=name,
            description=description,
            members_count=0,
            posts_count=0
        )
        
        self.db.add(community)
        await self.db.commit()
        
        return community
    
    async def update_community(
        self, 
        user_id: int, 
        community_id: int, 
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> CommunityModel:
        """
        Обновление информации о сообществе (только для администраторов).
        """
        
        community = await self.get_community_by_id(community_id)
        
        # Обновляем поля
        if name is not None:
            # Проверяем уникальность нового имени
            if name != community.name:
                stmt = select(CommunityModel).where(
                    and_(
                        CommunityModel.name == name,
                        CommunityModel.id != community_id
                    )
                )
                result = await self.db.execute(stmt)
                existing = result.scalar_one_or_none()
                if existing:
                    raise CommunityAlreadyExistsError()
            community.name = name
        
        if description is not None:
            community.description = description
        
        await self.db.commit()
        return community
    
    async def delete_community(self, user_id: int, community_id: int) -> None:
        """
        Удаление сообщества (только для администраторов).
        """
        
        community = await self.get_community_by_id(community_id)
        
        # Сначала удаляем всех участников
        stmt = select(UserCommunityModel).where(
            UserCommunityModel.community_id == community_id
        )
        result = await self.db.execute(stmt)
        members = result.scalars().all()
        
        for member in members:
            await self.db.delete(member)
        
        # Удаляем само сообщество
        await self.db.delete(community)
        await self.db.commit()
    
    async def get_statistics(self) -> dict:
        """
        Получение статистики по сообществам (только для администраторов).
        """
        # Общее количество сообществ
        total_stmt = select(func.count(CommunityModel.id))
        total_result = await self.db.execute(total_stmt)
        total_communities = total_result.scalar_one()
        
        # Общее количество участников
        members_stmt = select(func.sum(CommunityModel.members_count))
        members_result = await self.db.execute(members_stmt)
        total_members = members_result.scalar_one() or 0
        
        # Общее количество постов
        posts_stmt = select(func.sum(CommunityModel.posts_count))
        posts_result = await self.db.execute(posts_stmt)
        total_posts = posts_result.scalar_one() or 0
        
        # Топ сообществ по количеству участников
        top_stmt = select(CommunityModel).order_by(
            CommunityModel.members_count.desc()
        ).limit(10)
        top_result = await self.db.execute(top_stmt)
        top_communities = [
            {
                "id": c.id,
                "name": c.name,
                "members_count": c.members_count,
                "posts_count": c.posts_count
            }
            for c in top_result.scalars().all()
        ]
        
        return {
            "total_communities": total_communities,
            "total_members": total_members,
            "total_posts": total_posts,
            "top_communities": top_communities
        }