from fastapi import HTTPException
from app.repositories.favorites import FavoritesRepository
from app.repositories.posts import PostsRepository
from app.schemes.favorites import SFavoritePostCheck


class FavoritesService:
    """Сервис для работы с избранными постами"""
    
    def __init__(self, favorites_repo: FavoritesRepository, posts_repo: PostsRepository):
        self.favorites_repo = favorites_repo
        self.posts_repo = posts_repo

    async def add_to_favorites(self, user_id: int, post_id: int) -> dict:
        """Добавляет пост в избранное"""
        # Проверяем, существует ли пост
        post = await self.posts_repo.get(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Пост не найден")
        
        # Проверяем, не находится ли уже в избранном
        if await self.favorites_repo.is_favorite(user_id, post_id):
            return {"success": False, "message": "Пост уже в избранном", "is_favorite": True}
        
        # Добавляем в избранное
        success = await self.favorites_repo.add_favorite(user_id, post_id)
        if success:
            return {"success": True, "message": "Пост добавлен в избранное", "is_favorite": True}
        else:
            raise HTTPException(status_code=500, detail="Не удалось добавить пост в избранное")

    async def remove_from_favorites(self, user_id: int, post_id: int) -> dict:
        """Удаляет пост избранного"""
        # Проверяем, существует ли пост
        post = await self.posts_repo.get(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Пост не найден")
        
        # Проверяем, находится ли в избранном
        if not await self.favorites_repo.is_favorite(user_id, post_id):
            return {"success": False, "message": "Пост не в избранном", "is_favorite": False}
        
        # Удаляем из избранного
        success = await self.favorites_repo.remove_favorite(user_id, post_id)
        if success:
            return {"success": True, "message": "Пост удален из избранного", "is_favorite": False}
        else:
            raise HTTPException(status_code=500, detail="Не удалось удалить пост из избранного")

    async def toggle_favorite(self, user_id: int, post_id: int) -> dict:
        """Переключает состояние избранного для поста"""
        # Проверяем, существует ли пост
        post = await self.posts_repo.get(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Пост не найден")
        
        is_favorite = await self.favorites_repo.is_favorite(user_id, post_id)
        
        if is_favorite:
            # Удаляем из избранного
            success = await self.favorites_repo.remove_favorite(user_id, post_id)
            if success:
                return {"success": True, "message": "Пост удален из избранного", "is_favorite": False}
            else:
                raise HTTPException(status_code=500, detail="Не удалось удалить пост из избранного")
        else:
            # Добавляем в избранное
            success = await self.favorites_repo.add_favorite(user_id, post_id)
            if success:
                return {"success": True, "message": "Пост добавлен в избранное", "is_favorite": True}
            else:
                raise HTTPException(status_code=500, detail="Не удалось добавить пост в избранное")

    async def is_favorite(self, user_id: int, post_id: int) -> SFavoritePostCheck:
        """Проверяет, находится ли пост в избранном"""
        is_favorite = await self.favorites_repo.is_favorite(user_id, post_id)
        return SFavoritePostCheck(post_id=post_id, is_favorite=is_favorite)

    async def get_user_favorites(self, user_id: int, skip: int = 0, limit: int = 100) -> list:
        """Получает список избранных постов пользователя"""
        favorites = await self.favorites_repo.get_user_favorites(user_id, skip, limit)
        return favorites

    async def get_favorite_post_ids(self, user_id: int) -> list:
        """Получает список ID избранных постов пользователя"""
        post_ids = await self.favorites_repo.get_favorite_post_ids(user_id)
        return list(post_ids)