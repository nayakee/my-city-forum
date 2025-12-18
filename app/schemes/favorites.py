from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SFavoritePostCreate(BaseModel):
    """Схема для добавления поста в избранное"""
    post_id: int


class SFavoritePostGet(BaseModel):
    """Схема для получения информации об избранном посте"""
    user_id: int
    post_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class SFavoritePostDelete(BaseModel):
    """Схема для удаления поста из избранного"""
    post_id: int


class SFavoritePostCheck(BaseModel):
    """Схема для проверки, находится ли пост в избранном"""
    post_id: int
    is_favorite: bool