from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.models.comments import CommentModel
from app.repositories.base import BaseRepository
from app.schemes.comments import SCommentGet


class CommentsRepository(BaseRepository):
    """Репозиторий для работы с комментариями"""
    
    model = CommentModel
    schema = SCommentGet
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_post(
        self, 
        post_id: int,
        skip: int = 0, 
        limit: int = 100
    ) -> List[CommentModel]:
        """Получение комментариев поста"""
        query = (
            select(CommentModel)
            .where(CommentModel.post_id == post_id)
            .order_by(CommentModel.created_at)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_user(
        self, 
        user_id: int,
        skip: int = 0, 
        limit: int = 100
    ) -> List[CommentModel]:
        """Получение комментариев пользователя"""
        query = (
            select(CommentModel)
            .where(CommentModel.user_id == user_id)
            .order_by(desc(CommentModel.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()