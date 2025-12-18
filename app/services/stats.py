from typing import Dict, Any
from sqlalchemy import select, func, text
from app.database.db_manager import DBManager
from app.repositories.posts import PostsRepository
from app.repositories.users import UsersRepository
from app.repositories.comments import CommentsRepository
from app.repositories.communities import CommunitiesRepository
from app.repositories.themes import ThemesRepository


class StatsService:
    """Сервис для работы со статистикой приложения"""
    
    def __init__(self, db_manager: DBManager):
        self.db_manager = db_manager
        self.posts_repo = PostsRepository(db_manager.session)
        self.users_repo = UsersRepository(db_manager.session)
        self.comments_repo = CommentsRepository(db_manager.session)
        self.communities_repo = CommunitiesRepository(db_manager.session)
        self.themes_repo = ThemesRepository(db_manager.session)
    
    async def get_forum_stats(self) -> Dict[str, Any]:
        """Получение общей статистики форума"""
        # Подсчет пользователей
        users_count_query = select(func.count(self.users_repo.model.id))
        users_result = await self.db_manager.session.execute(users_count_query)
        total_users = users_result.scalar()
        
        # Подсчет постов
        posts_count_query = select(func.count(self.posts_repo.model.id))
        posts_result = await self.db_manager.session.execute(posts_count_query)
        total_posts = posts_result.scalar()
        
        # Подсчет комментариев
        comments_count_query = select(func.count(self.comments_repo.model.id))
        comments_result = await self.db_manager.session.execute(comments_count_query)
        total_comments = comments_result.scalar()
        
        # Подсчет сообществ
        communities_count_query = select(func.count(self.communities_repo.model.id))
        communities_result = await self.db_manager.session.execute(communities_count_query)
        total_communities = communities_result.scalar()
        
        # Подсчет тем
        themes_count_query = select(func.count(self.themes_repo.model.id))
        themes_result = await self.db_manager.session.execute(themes_count_query)
        total_themes = themes_result.scalar()
        
        # Подсчет лайков/дизлайков (используем SQL для суммирования)
        likes_dislikes_query = text("""
            SELECT 
                COALESCE(SUM(likes), 0) as total_likes,
                COALESCE(SUM(dislikes), 0) as total_dislikes
            FROM posts
        """)
        reactions_result = await self.db_manager.session.execute(likes_dislikes_query)
        reactions_row = reactions_result.mappings().first()
        
        total_reactions = (reactions_row['total_likes'] or 0) + (reactions_row['total_dislikes'] or 0)
        
        return {
            "total_users": total_users or 0,
            "total_posts": total_posts or 0,
            "total_comments": total_comments or 0,
            "total_communities": total_communities or 0,
            "total_themes": total_themes or 0,
            "total_reactions": total_reactions
        }
    
    async def get_theme_stats(self) -> Dict[str, Any]:
        """Получение статистики по темам"""
        # Получаем количество постов в каждой теме
        themes_query = text("""
            SELECT 
                t.id,
                t.name,
                COALESCE(t.posts_count, 0) as posts_count
            FROM themes t
            ORDER BY t.posts_count DESC
        """)
        
        result = await self.db_manager.session.execute(themes_query)
        themes_data = result.mappings().all()
        
        theme_stats = {}
        for theme in themes_data:
            # Приводим имена тем к нижнему регистру для соответствия шаблону
            theme_name_lower = theme['name'].lower()
            theme_stats[f"{theme_name_lower}_count"] = theme['posts_count']
        
        return theme_stats