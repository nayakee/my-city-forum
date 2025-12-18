from sqlalchemy import select
from fastapi import HTTPException
from app.models.posts import PostModel

class PostReactionService:
    @staticmethod
    async def toggle_reaction(
        db_session,
        user_id: int,
        post_id: int,
        reaction_type: str  # 'like' или 'dislike'
    ) -> dict:
        """
        Переключает реакцию пользователя на посте.
        Возвращает: {'action': 'added'/'removed'/'changed', 'likes': int, 'dislikes': int}
        """
        # Получаем пост
        result = await db_session.execute(
            select(PostModel).where(PostModel.id == post_id)
        )
        post = result.scalar_one_or_none()
        
        if not post:
            raise HTTPException(status_code=404, detail="Пост не найден")
        
        current_reaction = post.get_user_reaction(user_id)
        
        if current_reaction is None:
            # Нет реакции - добавляем новую
            if reaction_type == 'like':
                post.add_like(user_id)
                action = "added"
            else:
                post.add_dislike(user_id)
                action = "added"
                
        elif current_reaction == reaction_type:
            # Такая же реакция уже есть - удаляем её
            if reaction_type == 'like':
                post.remove_like(user_id)
                action = "removed"
            else:
                post.remove_dislike(user_id)
                action = "removed"
                
        else:
            # Противоположная реакция - меняем на новую
            if reaction_type == 'like':
                # Был дизлайк, ставим лайк
                post.remove_dislike(user_id)
                post.add_like(user_id)
                action = "changed"
            else:
                # Был лайк, ставим дизлайк
                post.remove_like(user_id)
                post.add_dislike(user_id)
                action = "changed"
        
        await db_session.commit()
        
        return {
            "action": action,
            "likes": post.likes or 0,
            "dislikes": post.dislikes or 0,
            "user_reaction": post.get_user_reaction(user_id)
        }
    
    @staticmethod
    async def get_user_reaction(
        db_session,
        user_id: int,
        post_id: int
    ) -> dict:
        """Получает реакцию пользователя на пост"""
        result = await db_session.execute(
            select(PostModel).where(PostModel.id == post_id)
        )
        post = result.scalar_one_or_none()
        
        if not post:
            raise HTTPException(status_code=404, detail="Пост не найден")
        
        reaction = post.get_user_reaction(user_id)
        
        return {
            "reaction_type": reaction,
            "has_liked": post.has_user_liked(user_id),
            "has_disliked": post.has_user_disliked(user_id),
            "likes": post.likes or 0,
            "dislikes": post.dislikes or 0
        }
    
    @staticmethod
    async def get_post_stats(
        db_session,
        post_id: int
    ) -> dict:
        """Получает статистику поста"""
        result = await db_session.execute(
            select(PostModel).where(PostModel.id == post_id)
        )
        post = result.scalar_one_or_none()
        
        if not post:
            raise HTTPException(status_code=404, detail="Пост не найден")
        
        reactions = post.reactions_dict
        
        return {
            "likes": post.likes or 0,
            "dislikes": post.dislikes or 0,
            "total_liked_by": len(reactions.get("liked_by", [])),
            "total_disliked_by": len(reactions.get("disliked_by", [])),
            "total_reactions": len(reactions.get("liked_by", [])) + len(reactions.get("disliked_by", []))
        }