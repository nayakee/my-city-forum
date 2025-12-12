from typing import Optional
from fastapi import APIRouter, Depends, Query

from app.api.dependencies import DBDep, CurrentUserDep
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
    current_user: CurrentUserDep,
) -> dict[str, str]:
    try:
        await PostService(db).create_post(post_data, current_user.id)
    except PostAlreadyExistsError:
        raise PostAlreadyExistsHTTPError
    
    return {"status": "OK", "message": "Пост успешно создан"}


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
) -> list[SPostGetWithComments]:
    posts = await PostService(db).get_posts_with_details(
        skip=skip,
        limit=limit,
        theme_id=theme_id,
        community_id=community_id
    )
    
    # Преобразуем результат в словари
    result = []
    for post, user_name, theme_name, community_name, comments_count in posts:
        post_dict = post.__dict__.copy()
        post_dict["user_name"] = user_name
        post_dict["theme_name"] = theme_name
        post_dict["community_name"] = community_name
        post_dict["comments_count"] = comments_count
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
    current_user: CurrentUserDep,
    post_id: int,
) -> dict[str, str]:
    try:
        await PostService(db).update_post(
            post_id=post_id,
            post_data=post_data,
            user_id=current_user.id,
            is_admin=getattr(current_user, "is_admin", False)  # Безопасное получение атрибута
        )
    except PostNotFoundError:
        raise PostNotFoundHTTPError
    except PostAccessDeniedError:
        raise PostAccessDeniedHTTPError
    
    return {"status": "OK", "message": "Пост успешно обновлен"}


@router.delete("/{post_id}", summary="Удаление поста")
async def delete_post(
    db: DBDep,
    current_user: CurrentUserDep,
    post_id: int,
) -> dict[str, str]:
    try:
        await PostService(db).delete_post(
            post_id=post_id,
            user_id=current_user.id,
            is_admin=getattr(current_user, "is_admin", False)  # Безопасное получение атрибута
        )
    except PostNotFoundError:
        raise PostNotFoundHTTPError
    except PostAccessDeniedError:
        raise PostAccessDeniedHTTPError
    
    return {"status": "OK", "message": "Пост успешно удален"}


@router.post("/{post_id}/like", summary="Лайк поста")
async def like_post(
    db: DBDep,
    post_id: int,
) -> dict[str, str]:
    post = await PostService(db).get_post(post_id)
    if not post:
        raise PostNotFoundHTTPError
    
    await PostService(db).like_post(post_id)
    return {"status": "OK", "message": "Лайк добавлен"}


@router.post("/{post_id}/dislike", summary="Дизлайк поста")
async def dislike_post(
    db: DBDep,
    post_id: int,
) -> dict[str, str]:
    post = await PostService(db).get_post(post_id)
    if not post:
        raise PostNotFoundHTTPError
    
    await PostService(db).dislike_post(post_id)
    return {"status": "OK", "message": "Дизлайк добавлен"}