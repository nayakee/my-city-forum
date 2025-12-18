from fastapi import APIRouter, Depends, HTTPException

from app.services.favorites import FavoritesService
from app.repositories.favorites import FavoritesRepository
from app.repositories.posts import PostsRepository
from app.schemes.favorites import (
    SFavoritePostCreate,
    SFavoritePostDelete,
    SFavoritePostCheck
)
from app.api.dependencies import get_current_user, get_db, DBDep
from app.models.users import UserModel

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.post("/add", summary="Добавить пост в избранное")
async def add_to_favorites(
    favorite_data: SFavoritePostCreate,
    db: DBDep,
    current_user: UserModel = Depends(get_current_user)
):
    """Добавляет пост в избранное для текущего пользователя"""
    favorites_repo = FavoritesRepository(db.session)
    posts_repo = PostsRepository(db.session)
    favorites_service = FavoritesService(favorites_repo, posts_repo)
    
    result = await favorites_service.add_to_favorites(current_user.id, favorite_data.post_id)
    return result


@router.post("/remove", summary="Удалить пост из избранного")
async def remove_from_favorites(
    favorite_data: SFavoritePostDelete,
    db: DBDep,
    current_user: UserModel = Depends(get_current_user)
):
    """Удаляет пост избранного текущего пользователя"""
    favorites_repo = FavoritesRepository(db.session)
    posts_repo = PostsRepository(db.session)
    favorites_service = FavoritesService(favorites_repo, posts_repo)
    
    result = await favorites_service.remove_from_favorites(current_user.id, favorite_data.post_id)
    return result


@router.post("/toggle", summary="Переключить состояние избранного")
async def toggle_favorite(
    favorite_data: SFavoritePostCreate,
    db: DBDep,
    current_user: UserModel = Depends(get_current_user)
):
    """Переключает состояние избранного для поста (добавить/удалить)"""
    favorites_repo = FavoritesRepository(db.session)
    posts_repo = PostsRepository(db.session)
    favorites_service = FavoritesService(favorites_repo, posts_repo)
    
    result = await favorites_service.toggle_favorite(current_user.id, favorite_data.post_id)
    return result


@router.get("/check/{post_id}", summary="Проверить, в избранном ли пост")
async def check_favorite(
    post_id: int,
    db: DBDep,
    current_user: UserModel = Depends(get_current_user)
):
    """Проверяет, находится ли пост в избранном у текущего пользователя"""
    favorites_repo = FavoritesRepository(db.session)
    posts_repo = PostsRepository(db.session)
    favorites_service = FavoritesService(favorites_repo, posts_repo)
    
    result = await favorites_service.is_favorite(current_user.id, post_id)
    return result


@router.get("/my", summary="Получить избранные посты пользователя")
async def get_user_favorites(
    db: DBDep,
    skip: int = 0,
    limit: int = 10,
    current_user: UserModel = Depends(get_current_user)
):
    """Получает список избранных постов текущего пользователя"""
    favorites_repo = FavoritesRepository(db.session)
    posts_repo = PostsRepository(db.session)
    favorites_service = FavoritesService(favorites_repo, posts_repo)
    
    favorites = await favorites_service.get_user_favorites(current_user.id, skip, limit)
    return favorites