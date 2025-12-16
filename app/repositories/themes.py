from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, text
from sqlalchemy.orm import selectinload
from app.models.themes import ThemeModel
from app.models.posts import PostModel
from app.repositories.base import BaseRepository


from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, text
from sqlalchemy.orm import selectinload

from app.models.themes import ThemeModel
from app.models.posts import PostModel
from app.repositories.base import BaseRepository
from app.schemes.themes import SThemeGet


class ThemesRepository(BaseRepository):
    """Репозиторий для работы с темами"""
    
    model = ThemeModel
    schema = SThemeGet
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_name(self, name: str) -> Optional[ThemeModel]:
        """Получение темы по имени"""
        query = select(ThemeModel).where(ThemeModel.name == name)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_with_posts(self, theme_id: int) -> Optional[Dict[str, Any]]:
        """Получение темы с постами"""
        query = (
            select(ThemeModel)
            .where(ThemeModel.id == theme_id)
            .options(selectinload(ThemeModel.posts))
        )
        result = await self.session.execute(query)
        theme = result.scalar_one_or_none()
        
        if not theme:
            return None
        
        return {
            "id": theme.id,
            "name": theme.name,
            "posts_count": theme.posts_count,
            "posts": theme.posts
        }

    async def get_popular_themes(
        self, 
        limit: int = 10
    ) -> List[ThemeModel]:
        """Получение популярных тем (по количеству постов)"""
        query = (
            select(ThemeModel)
            .order_by(desc(ThemeModel.posts_count))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def search_themes(
        self, 
        search_term: str,
        skip: int = 0, 
        limit: int = 100
    ) -> List[ThemeModel]:
        """Поиск тем по названию"""
        query = (
            select(ThemeModel)
            .where(ThemeModel.name.ilike(f"%{search_term}%"))
            .order_by(ThemeModel.name)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_themes_with_stats(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Получение тем со статистикой"""
        # Получаем темы с количеством активных постов (за последние 30 дней)
        query = text("""
            SELECT 
                t.id,
                t.name,
                t.posts_count,
                COUNT(p.id) as active_posts_last_month
            FROM themes t
            LEFT JOIN posts p ON t.id = p.theme_id 
                AND p.created_at >= datetime('now', '-30 days')
            GROUP BY t.id, t.name, t.posts_count
            ORDER BY t.posts_count DESC
            LIMIT :limit OFFSET :skip
        """)
        
        result = await self.session.execute(
            query, 
            {"skip": skip, "limit": limit}
        )
        
        themes_stats = []
        for row in result.mappings():
            themes_stats.append(dict(row))
        
        return themes_stats

    async def increment_posts_count(self, theme_id: int) -> None:
        """Увеличение счетчика постов в теме"""
        theme = await self.get(theme_id)
        if theme:
            theme.posts_count = (theme.posts_count or 0) + 1
            await self.session.flush()

    async def decrement_posts_count(self, theme_id: int) -> None:
        """Уменьшение счетчика постов в теме"""
        theme = await self.get(theme_id)
        if theme and theme.posts_count > 0:
            theme.posts_count = theme.posts_count - 1
            await self.session.flush()

    async def get_theme_stats(self, theme_id: int) -> Dict[str, Any]:
        """Получение подробной статистики по теме"""
        # Получаем тему
        theme = await self.get(theme_id)
        if not theme:
            return {}
        
        # Статистика по постам за разные периоды
        stats_query = text("""
            SELECT 
                COUNT(*) as total_posts,
                SUM(CASE WHEN created_at >= datetime('now', '-7 days') THEN 1 ELSE 0 END) as posts_last_week,
                SUM(CASE WHEN created_at >= datetime('now', '-30 days') THEN 1 ELSE 0 END) as posts_last_month,
                AVG(likes) as avg_likes,
                AVG(dislikes) as avg_dislikes
            FROM posts 
            WHERE theme_id = :theme_id
        """)
        
        result = await self.session.execute(
            stats_query, 
            {"theme_id": theme_id}
        )
        
        stats = result.mappings().first()
        
        return {
            "theme_id": theme_id,
            "theme_name": theme.name,
            "total_posts": theme.posts_count or 0,
            "stats": dict(stats) if stats else {}
        }

    async def get_themes_usage_over_time(
        self, 
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Получение статистики использования тем за период"""
        query = text("""
            SELECT 
                t.id,
                t.name,
                COUNT(p.id) as posts_count,
                DATE(p.created_at) as post_date
            FROM themes t
            LEFT JOIN posts p ON t.id = p.theme_id 
                AND p.created_at >= datetime('now', :days_param || ' days')
            WHERE p.id IS NOT NULL
            GROUP BY t.id, t.name, DATE(p.created_at)
            ORDER BY post_date DESC, posts_count DESC
        """)
        
        result = await self.session.execute(
            query, 
            {"days_param": f"-{days}"}
        )
        
        usage_stats = []
        for row in result.mappings():
            usage_stats.append(dict(row))
        
        return usage_stats

    async def bulk_update_posts_count(self) -> None:
        """Обновление счетчиков постов для всех тем (синхронизация)"""
        # Получаем актуальные счетчики из таблицы постов
        count_query = text("""
            SELECT theme_id, COUNT(*) as actual_count
            FROM posts
            GROUP BY theme_id
        """)
        
        result = await self.session.execute(count_query)
        theme_counts = {row.theme_id: row.actual_count for row in result}
        
        # Обновляем счетчики в таблице тем
        all_themes = await self.get_all()
        for theme in all_themes:
            actual_count = theme_counts.get(theme.id, 0)
            if theme.posts_count != actual_count:
                theme.posts_count = actual_count
        
        await self.session.flush()