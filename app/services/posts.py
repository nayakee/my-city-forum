from datetime import datetime
from typing import Optional
from sqlalchemy import select, update, delete, func

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
    def __init__(self, db):
        self.db = db  # DBManager instance

    async def create_post(self, post_data: SPostAdd, user_id: int) -> PostModel:
        """Создание нового поста"""
        return await self.create_post_with_community_update(post_data, user_id)

    async def create_post_web(self, post_data: SPostAdd, user_id: int) -> PostModel:
        """Создание нового поста через веб-интерфейс с валидацией"""
        # Валидация данных
        if not post_data.header or not post_data.body or not post_data.theme_id:
            raise ValueError("Заголовок, содержание и тема обязательны для заполнения")
        
        if len(post_data.header) > 200:
            raise ValueError("Заголовок должен быть не более 200 символов")
        
        if len(post_data.body) > 5000:
            raise ValueError("Содержание должно быть не более 5000 символов")
        
        # Проверяем существование темы
        theme = await self.db.themes.get(post_data.theme_id)
        if not theme:
            raise ValueError("Выбранная тема не существует")
        
        # Создаем пост
        return await self.create_post_with_community_update(post_data, user_id)
    
    async def get_post(self, post_id: int) -> Optional[PostModel]:
        """Получение поста по ID"""
        return await self.db.posts.get(post_id)

    async def get_posts(
        self,
        skip: int = 0,
        limit: int = 100,
        theme_id: Optional[int] = None,
        community_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> list[PostModel]:
        """Получение списка постов с фильтрацией"""
        filters = {}
        if theme_id:
            filters['theme_id'] = theme_id
        if community_id:
            filters['community_id'] = community_id
        if user_id:
            filters['user_id'] = user_id
            
        return await self.db.posts.get_filtered(
            **filters,
            offset=skip,
            limit=limit
        )

    async def get_posts_with_details(
        self,
        skip: int = 0,
        limit: int = 100,
        theme_id: Optional[int] = None,
        community_id: Optional[int] = None
    ) -> list[dict]:
        """Получение постов с дополнительной информацией (автор, тема, сообщество)"""
        # Получаем посты с фильтрацией
        filters = {}
        if theme_id:
            filters['theme_id'] = theme_id
        if community_id:
            filters['community_id'] = community_id
            
        posts = await self.db.posts.get_filtered(
            **filters,
            offset=skip,
            limit=limit
        )
        
        # Для каждого поста получаем дополнительную информацию
        result = []
        for post in posts:
            user = await self.db.users.get(post.user_id)
            theme = await self.db.themes.get(post.theme_id)
            community = await self.db.communities.get(post.community_id) if post.community_id else None
            
            # Получаем количество комментариев к посту
            comments = await self.db.comments.get_filtered(post_id=post.id)
            comments_count = len(comments)
            
            post_dict = post.__dict__.copy()
            post_dict["user_name"] = user.name if user else "Unknown"
            post_dict["theme_name"] = theme.name if theme else "Unknown"
            post_dict["community_name"] = community.name if community else "Unknown"
            post_dict["comments_count"] = comments_count
            result.append(post_dict)
        
        return result

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
        
        # Обновляем пост
        update_data = post_data.model_dump(exclude_unset=True)
        if update_data:
            await self.db.posts.edit(update_data, id=post_id)

    async def delete_post(
        self,
        post_id: int,
        user_id: int,
        is_admin: bool = False
    ) -> None:
        """Удаление поста (только автор или админ) с обновлением счетчика в сообществе"""
        post = await self.get_post(post_id)
        if not post:
            raise PostNotFoundError
        
        # Проверка прав доступа
        if not is_admin and post.user_id != user_id:
            raise PostAccessDeniedError
        
        # Запоминаем ID сообщества перед удалением
        community_id = post.community_id
        
        await self.db.posts.delete(id=post_id)
        
        # Уменьшаем счетчик постов в сообществе
        if community_id:
            from app.services.communities import CommunitiesService
            await CommunitiesService(self.db).decrement_posts_count(community_id)

    async def like_post(self, post_id: int) -> None:
        """Добавление лайка посту"""
        post = await self.db.posts.get(post_id)
        if post:
            update_data = {"likes": (post.likes or 0) + 1}
            await self.db.posts.edit(update_data, id=post_id)

    async def dislike_post(self, post_id: int) -> None:
        """Добавление дизлайка посту"""
        post = await self.db.posts.get(post_id)
        if post:
            update_data = {"dislikes": (post.dislikes or 0) + 1}
            await self.db.posts.edit(update_data, id=post_id)

# app/services/posts.py (дополнение к ранее созданному)

    async def create_post_with_community_update(self, post_data: SPostAdd, user_id: int) -> PostModel:
        """Создание нового поста с обновлением счетчика в сообществе"""
        post_data_dict = post_data.model_dump()
        post_data_dict['user_id'] = user_id
        post_data_dict['created_at'] = datetime.utcnow()
        post_data_dict['likes'] = 0
        post_data_dict['dislikes'] = 0
        
        new_post = await self.db.posts.add(post_data_dict)
        
        # Увеличиваем счетчик постов в сообществе, если пост привязан к сообществу
        if post_data.community_id:
            from app.services.communities import CommunitiesService
            await CommunitiesService(self.db).increment_posts_count(post_data.community_id)
        
        return new_post

    async def get_posts_for_web(
        self,
        skip: int = 0,
        limit: int = 100,
        theme_id: Optional[int] = None,
        community_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> list[dict]:
        """Получение списка постов с фильтрацией и дополнительной информацией для веб-страницы"""
        filters = {}
        if theme_id:
            filters['theme_id'] = theme_id
        if community_id:
            filters['community_id'] = community_id
        if user_id:
            filters['user_id'] = user_id
            
        posts = await self.db.posts.get_filtered(
            **filters,
            offset=skip,
            limit=limit
        )
        
        # Для каждого поста получаем дополнительную информацию
        result = []
        for post in posts:
            user = await self.db.users.get(post.user_id)
            theme = await self.db.themes.get(post.theme_id)
            community = await self.db.communities.get(post.community_id) if post.community_id else None
            
            post_dict = post.__dict__.copy()
            post_dict["user_name"] = user.name if user else "Unknown"
            post_dict["theme_name"] = theme.name if theme else "Unknown"
            post_dict["community_name"] = community.name if community else "Unknown"
            result.append(post_dict)
            
        return result