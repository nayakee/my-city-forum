from datetime import datetime
from typing import Optional
from sqlalchemy import select, update, delete, func

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
    def __init__(self, db):
        self.db = db  # DBManager instance

    async def create_comment(self, comment_data: SCommentAdd, user_id: int) -> CommentModel:
        """Создание нового комментария"""
        # Проверяем, существует ли пост
        post = await self.db.posts.get(comment_data.post_id)
        if not post:
            raise CommentToDeletedPostError
        
        comment_data_dict = comment_data.model_dump()
        comment_data_dict['user_id'] = user_id
        comment_data_dict['created_at'] = datetime.utcnow()
        comment_data_dict['likes'] = 0
        comment_data_dict['dislikes'] = 0
        
        new_comment = await self.db.comments.add(comment_data_dict)
        return new_comment

    async def get_comment(self, comment_id: int) -> Optional[CommentModel]:
        """Получение комментария по ID"""
        return await self.db.comments.get(comment_id)

    async def get_comments_by_post(
        self,
        post_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> list[CommentModel]:
        """Получение комментариев к конкретному посту"""
        return await self.db.comments.get_filtered(
            post_id=post_id,
            offset=skip,
            limit=limit
        )

    async def get_comments_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> list[CommentModel]:
        """Получение комментариев конкретного пользователя"""
        return await self.db.comments.get_filtered(
            user_id=user_id,
            offset=skip,
            limit=limit
        )

    async def get_comments_with_details(
        self,
        post_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> list[dict]:
        """Получение комментариев с дополнительной информацией"""
        # Сначала получаем комментарии
        comments = await self.db.comments.get_filtered(
            post_id=post_id,
            offset=skip,
            limit=limit
        )
        
        # Затем для каждого комментария получаем дополнительные данные
        result = []
        for comment in comments:
            user = await self.db.users.get(comment.user_id)
            post = await self.db.posts.get(comment.post_id)
            
            comment_dict = comment.__dict__.copy()
            comment_dict["user_name"] = user.username if user else "Unknown"
            comment_dict["post_header"] = post.header if post else "Unknown"
            result.append(comment_dict)
        
        return result

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
        
        # Обновляем комментарий
        update_data = comment_data.model_dump(exclude_unset=True)
        if update_data:
            await self.db.comments.edit(update_data, id=comment_id)

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
        
        await self.db.comments.delete(id=comment_id)

    async def like_comment(self, comment_id: int) -> None:
        """Добавление лайка комментарию"""
        comment = await self.db.comments.get(comment_id)
        if comment:
            update_data = {"likes": (comment.likes or 0) + 1}
            await self.db.comments.edit(update_data, id=comment_id)

    async def dislike_comment(self, comment_id: int) -> None:
        """Добавление дизлайка комментарию"""
        comment = await self.db.comments.get(comment_id)
        if comment:
            update_data = {"dislikes": (comment.dislikes or 0) + 1}
            await self.db.comments.edit(update_data, id=comment_id)

    async def get_comments_count_by_post(self, post_id: int) -> int:
        """Получение количества комментариев к посту"""
        comments = await self.db.comments.get_filtered(post_id=post_id)
        return len(comments)