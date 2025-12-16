from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException

from app.api.dependencies import DBDep, CurrentUserDep  # Используем CurrentUserDep вместо UserDepWithRole
from app.exceptions.posts import (
    PostNotFoundError,
    PostNotFoundHTTPError,
    PostAccessDeniedError,
    PostAccessDeniedHTTPError,
    PostAlreadyExistsError,
    PostAlreadyExistsHTTPError
)
from app.schemes.posts import SPostAdd, SPostUpdate, SPostGet, SPostGetWithComments
from app.services.posts import PostService

router = APIRouter(prefix="/posts", tags=["Посты"])


@router.post("", summary="Создание нового поста")
async def create_post(
    post_data: SPostAdd,
    db: DBDep,
    current_user = Depends(CurrentUserDep),  # Используем CurrentUserDep
) -> dict:
    try:
        # Проверяем, авторизован ли пользователь
        if not current_user:
            raise HTTPException(status_code=401, detail="Требуется авторизация")
        
        post = await PostService(db).create_post(post_data, current_user.id)
        return {
            "status": "OK",
            "message": "Пост успешно создан",
            "post_id": post.id
        }
    except PostAlreadyExistsError:
        raise PostAlreadyExistsHTTPError
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка создания поста: {str(e)}")


@router.get("", summary="Получение списка постов")
async def get_posts(
    db: DBDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    theme_id: Optional[int] = None,
    community_id: Optional[int] = None,
    user_id: Optional[int] = None,
) -> list[SPostGet]:
    posts = await PostService(db).get_posts(
        skip=skip,
        limit=limit,
        theme_id=theme_id,
        community_id=community_id,
        user_id=user_id
    )
    return posts


@router.get("/detailed", summary="Получение постов с детальной информацией")
async def get_posts_detailed(
    db: DBDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    theme_id: Optional[int] = None,
    community_id: Optional[int] = None,
) -> list[dict]:
    posts = await PostService(db).get_posts_with_details(
        skip=skip,
        limit=limit,
        theme_id=theme_id,
        community_id=community_id
    )
    
    # Преобразуем результат в словари
    result = []
    for post, user_name, theme_name, community_name, comments_count in posts:
        post_dict = {
            "id": post.id,
            "header": post.header,
            "body": post.body,
            "theme_id": post.theme_id,
            "community_id": post.community_id,
            "user_id": post.user_id,
            "is_published": post.is_published,
            "likes": post.likes,
            "dislikes": post.dislikes,
            "created_at": post.created_at,
            "updated_at": post.updated_at,
            "user_name": user_name,
            "theme_name": theme_name,
            "community_name": community_name,
            "comments_count": comments_count
        }
        result.append(post_dict)
    
    return result


@router.get("/{post_id}", summary="Получение конкретного поста")
async def get_post(
    db: DBDep,
    post_id: int,
) -> SPostGet:
    post = await PostService(db).get_post(post_id)
    if not post:
        raise PostNotFoundHTTPError
    return post


@router.put("/{post_id}", summary="Обновление поста")
async def update_post(
    post_data: SPostUpdate,
    db: DBDep,
    post_id: int,
    current_user = Depends(CurrentUserDep),  # Используем CurrentUserDep
) -> dict:
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Требуется авторизация")
        
        # Проверяем, является ли пользователь администратором
        is_admin = hasattr(current_user, 'role') and current_user.role.level >= 3
        
        await PostService(db).update_post(
            post_id=post_id,
            post_data=post_data,
            user_id=current_user.id,
            is_admin=is_admin
        )
        return {"status": "OK", "message": "Пост успешно обновлен"}
    except PostNotFoundError:
        raise PostNotFoundHTTPError
    except PostAccessDeniedError:
        raise PostAccessDeniedHTTPError


@router.delete("/{post_id}", summary="Удаление поста")
async def delete_post(
    db: DBDep,
    post_id: int,
    current_user = Depends(CurrentUserDep),  # Используем CurrentUserDep
) -> dict:
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Требуется авторизация")
        
        # Проверяем, является ли пользователь администратором
        is_admin = hasattr(current_user, 'role') and current_user.role.level >= 3
        
        await PostService(db).delete_post(
            post_id=post_id,
            user_id=current_user.id,
            is_admin=is_admin
        )
        return {"status": "OK", "message": "Пост успешно удален"}
    except PostNotFoundError:
        raise PostNotFoundHTTPError
    except PostAccessDeniedError:
        raise PostAccessDeniedHTTPError


@router.post("/{post_id}/like", summary="Лайк поста")
async def like_post(
    db: DBDep,
    post_id: int,
) -> dict:
    post = await PostService(db).get_post(post_id)
    if not post:
        raise PostNotFoundHTTPError
    
    await PostService(db).like_post(post_id)
    return {"status": "OK", "message": "Лайк добавлен"}


@router.post("/{post_id}/dislike", summary="Дизлайк поста")
async def dislike_post(
    db: DBDep,
    post_id: int,
) -> dict:
    post = await PostService(db).get_post(post_id)
    if not post:
        raise PostNotFoundHTTPError
    
    await PostService(db).dislike_post(post_id)
    return {"status": "OK", "message": "Дизлайк добавлен"}


@router.get("/{post_id}/comments/count", summary="Получение количества комментариев к посту")
async def get_post_comments_count(
    db: DBDep,
    post_id: int,
) -> dict:
    comments = await db.comments.get_filtered(post_id=post_id)
    return {"count": len(comments)}


# Endpoint'ы для веб-интерфейса с поддержкой пагинации через page/limit
@router.get("/web", summary="Получение списка постов для веб-интерфейса (с пагинацией page/limit)")
async def get_posts_web(
    db: DBDep,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    theme_id: Optional[int] = None,
    community_id: Optional[int] = None,
    user_id: Optional[int] = None,
) -> list[SPostGet]:
    skip = (page - 1) * limit
    posts = await PostService(db).get_posts(
        skip=skip,
        limit=limit,
        theme_id=theme_id,
        community_id=community_id,
        user_id=user_id
    )
    return posts


@router.get("/web/detailed", summary="Получение постов с детальной информацией для веб-интерфейса (с пагинацией page/limit)")
async def get_posts_detailed_web(
    db: DBDep,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    theme_id: Optional[int] = None,
    community_id: Optional[int] = None,
) -> list[dict]:
    skip = (page - 1) * limit
    posts = await PostService(db).get_posts_with_details(
        skip=skip,
        limit=limit,
        theme_id=theme_id,
        community_id=community_id
    )
    
    # Преобразуем результат в словари
    result = []
    for post, user_name, theme_name, community_name, comments_count in posts:
        post_dict = {
            "id": post.id,
            "header": post.header,
            "body": post.body,
            "theme_id": post.theme_id,
            "community_id": post.community_id,
            "user_id": post.user_id,
            "is_published": post.is_published,
            "likes": post.likes,
            "dislikes": post.dislikes,
            "created_at": post.created_at,
            "updated_at": post.updated_at,
            "user_name": user_name,
            "theme_name": theme_name,
            "community_name": community_name,
            "comments_count": comments_count
        }
        result.append(post_dict)
    
    return result