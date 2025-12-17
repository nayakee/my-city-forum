from typing import List, Optional
from app.models.themes import ThemeModel as Theme
from app.schemes.themes import SThemeCreate, SThemeUpdate


class ThemeService:
    def __init__(self, db):
        self.db = db  # DBManager instance

    async def get_theme(self, theme_id: int) -> Optional[Theme]:
        """Получить тему по ID"""
        return await self.db.themes.get(theme_id)

    async def get_themes(self, skip: int = 0, limit: int = 100) -> List[Theme]:
        """Получить список тем"""
        return await self.db.themes.get_all(offset=skip, limit=limit)

    async def create_theme(self, theme_data: SThemeCreate) -> Theme:
        """Создать новую тему"""
        theme_dict = theme_data.model_dump()
        theme_dict['posts_count'] = 0 # Новая тема не имеет постов
        return await self.db.themes.add(theme_dict)

    async def update_theme(self, theme_id: int, theme_data: SThemeUpdate) -> Optional[Theme]:
        """Обновить тему"""
        theme = await self.get_theme(theme_id)
        if not theme:
            return None
            
        update_data = theme_data.model_dump(exclude_unset=True)
        if update_data:
            await self.db.themes.edit(update_data, id=theme_id)
            
        return await self.get_theme(theme_id)

    async def delete_theme(self, theme_id: int) -> bool:
        """Удалить тему"""
        theme = await self.get_theme(theme_id)
        if not theme:
            return False
            
        await self.db.themes.delete(id=theme_id)
        return True

    async def get_theme_by_name(self, name: str) -> Optional[Theme]:
        """Получить тему по названию"""
        return await self.db.themes.get_by_name(name)

    async def get_themes_with_post_counts(self, skip: int = 0, limit: int = 100) -> List[dict]:
        """Получить список тем с подсчетом количества постов в каждой теме"""
        return await self.db.themes.get_themes_with_stats(skip=skip, limit=limit)

    async def get_theme_with_post_count(self, theme_id: int) -> Optional[dict]:
        """Получить тему с подсчетом количества постов"""
        # Получаем статистику по теме
        stats = await self.db.themes.get_theme_stats(theme_id)
        if not stats:
            return None
            
        # Получаем саму тему
        theme = await self.get_theme(theme_id)
        if not theme:
            return None
            
        # Объединяем данные
        result = theme.__dict__.copy()
        result['posts_count'] = stats.get('total_posts', 0)
        return result

    async def increment_posts_count(self, theme_id: int) -> None:
        """Увеличение счетчика постов в теме"""
        await self.db.themes.increment_posts_count(theme_id)

    async def decrement_posts_count(self, theme_id: int) -> None:
        """Уменьшение счетчика постов в теме"""
        await self.db.themes.decrement_posts_count(theme_id)