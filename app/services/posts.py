from datetime import datetime
from typing import Optional
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.posts import PostModel
from app.models.users import UserModel
from app.models.themes import ThemeModel
from app.models.communities import CommunityModel
from app.schemes.posts import SPostAdd, SPostUpdate, SPostGet
from app.exceptions.posts import (
    PostNotFoundError,
    PostAccessDeniedError,
    PostAlreadyExistsError
)


class PostService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_post(self, post_data: SPostAdd, user_id: int) -> PostModel:
        """Создание нового поста"""
        # Проверка на уникальность заголовка (если нужно)
        # query = select(PostModel).where(PostModel.header == post_data.header)
        # result = await self.db.execute(query)
        # if result.scalar_one_or_none():
        #     raise PostAlreadyExistsError
        
        new_post = PostModel(
            **post_data.model_dump(),
            user_id=user_id,
            created_at=datetime.utcnow(),
            likes=0,
            dislikes=0
        )
        
        self.db.add(new_post)
        await self.db.commit()
        await self.db.refresh(new_post)
        return new_post

    async def get_post(self, post_id: int) -> Optional[PostModel]:
        """Получение поста по ID"""
        query = select(PostModel).where(PostModel.id == post_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_posts(
        self, 
        skip: int = 0, 
        limit: int = 100,
        theme_id: Optional[int] = None,
        community_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> list[PostModel]:
        """Получение списка постов с фильтрацией"""
        query = select(PostModel)
        
        if theme_id:
            query = query.where(PostModel.theme_id == theme_id)
        if community_id:
            query = query.where(PostModel.community_id == community_id)
        if user_id:
            query = query.where(PostModel.user_id == user_id)
        
        query = query.offset(skip).limit(limit).order_by(PostModel.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_posts_with_details(
        self, 
        skip: int = 0, 
        limit: int = 100,
        theme_id: Optional[int] = None,
        community_id: Optional[int] = None
    ) -> list[dict]:
        """Получение постов с дополнительной информацией (автор, тема, сообщество)"""
        query = (
            select(
                PostModel,
                UserModel.username.label("user_name"),
                ThemeModel.name.label("theme_name"),
                CommunityModel.name.label("community_name"),
                func.count(PostModel.comments).label("comments_count")
            )
            .join(UserModel, PostModel.user_id == UserModel.id)
            .join(ThemeModel, PostModel.theme_id == ThemeModel.id)
            .outerjoin(CommunityModel, PostModel.community_id == CommunityModel.id)
            .group_by(PostModel.id, UserModel.id, ThemeModel.id, CommunityModel.id)
        )
        
        if theme_id:
            query = query.where(PostModel.theme_id == theme_id)
        if community_id:
            query = query.where(PostModel.community_id == community_id)
        
        query = query.offset(skip).limit(limit).order_by(PostModel.created_at.desc())
        
        result = await self.db.execute(query)
        return result.all()

    async def update_post(
        self, 
        post_id: int, 
        post_data: SPostUpdate, 
        user_id: int,
        is_admin: bool = False
    ) -> None:
        """Обновление поста (только автор или админ)"""
        post = await self.get_post(post_id)
        if not post:
            raise PostNotFoundError
        
        # Проверка прав доступа
        if not is_admin and post.user_id != user_id:
            raise PostAccessDeniedError
        
        # Обновляем только переданные поля
        update_data = post_data.model_dump(exclude_unset=True)
        if update_data:
            query = (
                update(PostModel)
                .where(PostModel.id == post_id)
                .values(**update_data)
            )
            await self.db.execute(query)
            await self.db.commit()

    async def delete_post(
        self, 
        post_id: int, 
        user_id: int,
        is_admin: bool = False
    ) -> None:
        """Удаление поста (только автор или админ)"""
        post = await self.get_post(post_id)
        if not post:
            raise PostNotFoundError
        
        # Проверка прав доступа
        if not is_admin and post.user_id != user_id:
            raise PostAccessDeniedError
        
        query = delete(PostModel).where(PostModel.id == post_id)
        await self.db.execute(query)
        await self.db.commit()

    async def like_post(self, post_id: int) -> None:
        """Добавление лайка посту"""
        query = (
            update(PostModel)
            .where(PostModel.id == post_id)
            .values(likes=PostModel.likes + 1)
        )
        await self.db.execute(query)
        await self.db.commit()

    async def dislike_post(self, post_id: int) -> None:
        """Добавление дизлайка посту"""
        query = (
            update(PostModel)
            .where(PostModel.id == post_id)
            .values(dislikes=PostModel.dislikes + 1)
        )
        await self.db.execute(query)
        await self.db.commit()

# app/services/posts.py (дополнение к ранее созданному)

async def create_post(self, post_data: SPostAdd, user_id: int) -> PostModel:
    """Создание нового поста"""
    new_post = PostModel(
        **post_data.model_dump(),
        user_id=user_id,
        created_at=datetime.utcnow(),
        likes=0,
        dislikes=0
    )
    
    self.db.add(new_post)
    await self.db.commit()
    await self.db.refresh(new_post)
    
    # Увеличиваем счетчик постов в сообществе, если пост привязан к сообществу
    if post_data.community_id:
        from app.services.communities import CommunitiesService
        await CommunitiesService(self.db).increment_posts_count(post_data.community_id)
    
    return new_post


async def delete_post(self, post_id: int, user_id: int, is_admin: bool = False) -> None:
    """Удаление поста"""
    post = await self.get_post(post_id)
    if not post:
        raise PostNotFoundError
    
    # Проверка прав доступа
    if not is_admin and post.user_id != user_id:
        raise PostAccessDeniedError
    
    # Запоминаем ID сообщества перед удалением
    community_id = post.community_id
    
    query = delete(PostModel).where(PostModel.id == post_id)
    await self.db.execute(query)
    await self.db.commit()
    
    # Уменьшаем счетчик постов в сообществе
    if community_id:
        from app.services.communities import CommunitiesService
        await CommunitiesService(self.db).decrement_posts_count(community_id)