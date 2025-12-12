from datetime import datetime
from typing import Optional
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comments import CommentModel
from app.models.posts import PostModel
from app.models.users import UserModel
from app.schemes.comments import SCommentAdd, SCommentUpdate
from app.exceptions.comments import (
    CommentNotFoundError,
    CommentAccessDeniedError,
    CommentToDeletedPostError
)


class CommentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_comment(self, comment_data: SCommentAdd, user_id: int) -> CommentModel:
        """Создание нового комментария"""
        # Проверяем, существует ли пост
        post_query = select(PostModel).where(PostModel.id == comment_data.post_id)
        post_result = await self.db.execute(post_query)
        post = post_result.scalar_one_or_none()
        
        if not post:
            raise CommentToDeletedPostError
        
        new_comment = CommentModel(
            **comment_data.model_dump(),
            user_id=user_id,
            created_at=datetime.utcnow(),
            likes=0,
            dislikes=0
        )
        
        self.db.add(new_comment)
        await self.db.commit()
        await self.db.refresh(new_comment)
        return new_comment

    async def get_comment(self, comment_id: int) -> Optional[CommentModel]:
        """Получение комментария по ID"""
        query = select(CommentModel).where(CommentModel.id == comment_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_comments_by_post(
        self, 
        post_id: int,
        skip: int = 0, 
        limit: int = 100
    ) -> list[CommentModel]:
        """Получение комментариев к конкретному посту"""
        query = (
            select(CommentModel)
            .where(CommentModel.post_id == post_id)
            .offset(skip)
            .limit(limit)
            .order_by(CommentModel.created_at.asc())  # Старые сверху
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_comments_by_user(
        self, 
        user_id: int,
        skip: int = 0, 
        limit: int = 100
    ) -> list[CommentModel]:
        """Получение комментариев конкретного пользователя"""
        query = (
            select(CommentModel)
            .where(CommentModel.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(CommentModel.created_at.desc())  # Новые сверху
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_comments_with_details(
        self, 
        post_id: int,
        skip: int = 0, 
        limit: int = 100
    ) -> list[dict]:
        """Получение комментариев с дополнительной информацией"""
        query = (
            select(
                CommentModel,
                UserModel.username.label("user_name"),
                PostModel.header.label("post_header")
            )
            .join(UserModel, CommentModel.user_id == UserModel.id)
            .join(PostModel, CommentModel.post_id == PostModel.id)
            .where(CommentModel.post_id == post_id)
            .offset(skip)
            .limit(limit)
            .order_by(CommentModel.created_at.asc())
        )
        
        result = await self.db.execute(query)
        return result.all()

    async def update_comment(
        self, 
        comment_id: int, 
        comment_data: SCommentUpdate, 
        user_id: int,
        is_admin: bool = False
    ) -> None:
        """Обновление комментария (только автор или админ)"""
        comment = await self.get_comment(comment_id)
        if not comment:
            raise CommentNotFoundError
        
        # Проверка прав доступа
        if not is_admin and comment.user_id != user_id:
            raise CommentAccessDeniedError
        
        # Обновляем только переданные поля
        update_data = comment_data.model_dump(exclude_unset=True)
        if update_data:
            query = (
                update(CommentModel)
                .where(CommentModel.id == comment_id)
                .values(**update_data)
            )
            await self.db.execute(query)
            await self.db.commit()

    async def delete_comment(
        self, 
        comment_id: int, 
        user_id: int,
        is_admin: bool = False
    ) -> None:
        """Удаление комментария (только автор или админ)"""
        comment = await self.get_comment(comment_id)
        if not comment:
            raise CommentNotFoundError
        
        # Проверка прав доступа
        if not is_admin and comment.user_id != user_id:
            raise CommentAccessDeniedError
        
        query = delete(CommentModel).where(CommentModel.id == comment_id)
        await self.db.execute(query)
        await self.db.commit()

    async def like_comment(self, comment_id: int) -> None:
        """Добавление лайка комментарию"""
        query = (
            update(CommentModel)
            .where(CommentModel.id == comment_id)
            .values(likes=CommentModel.likes + 1)
        )
        await self.db.execute(query)
        await self.db.commit()

    async def dislike_comment(self, comment_id: int) -> None:
        """Добавление дизлайка комментарию"""
        query = (
            update(CommentModel)
            .where(CommentModel.id == comment_id)
            .values(dislikes=CommentModel.dislikes + 1)
        )
        await self.db.execute(query)
        await self.db.commit()

    async def get_comments_count_by_post(self, post_id: int) -> int:
        """Получение количества комментариев к посту"""
        query = (
            select(func.count(CommentModel.id))
            .where(CommentModel.post_id == post_id)
        )
        result = await self.db.execute(query)
        return result.scalar()