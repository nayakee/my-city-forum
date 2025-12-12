from typing import Optional
from fastapi import APIRouter, Depends, Query, Path

from app.api.dependencies import DBDep, CurrentUserDep
from app.exceptions.comments import (
    CommentNotFoundError,
    CommentNotFoundHTTPError,
    CommentAccessDeniedError,
    CommentAccessDeniedHTTPError,
    CommentToDeletedPostError,
    CommentToDeletedPostHTTPError
)
from app.schemes.comments import SCommentAdd, SCommentUpdate, SCommentGet, SCommentGetWithReplies
from app.services.comments import CommentService

router = APIRouter(prefix="/comments", tags=["Комментарии"])


@router.post("", summary="Создание нового комментария")
async def create_comment(
    comment_data: SCommentAdd,
    db: DBDep,
    current_user: CurrentUserDep,
) -> dict[str, str]:
    try:
        await CommentService(db).create_comment(comment_data, current_user.id)
    except CommentToDeletedPostError:
        raise CommentToDeletedPostHTTPError
    
    return {"status": "OK", "message": "Комментарий успешно создан"}


@router.get("", summary="Получение всех комментариев пользователя")
async def get_user_comments(
    db: DBDep,
    current_user: CurrentUserDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> list[SCommentGet]:
    comments = await CommentService(db).get_comments_by_user(
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return comments


@router.get("/post/{post_id}", summary="Получение комментариев к посту")
async def get_post_comments(
    db: DBDep,
    post_id: int = Path(..., description="ID поста"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> list[SCommentGet]:
    comments = await CommentService(db).get_comments_by_post(
        post_id=post_id,
        skip=skip,
        limit=limit
    )
    return comments


@router.get("/post/{post_id}/detailed", summary="Получение комментариев к посту с детальной информацией")
async def get_post_comments_detailed(
    db: DBDep,
    post_id: int = Path(..., description="ID поста"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> list[SCommentGetWithReplies]:
    comments = await CommentService(db).get_comments_with_details(
        post_id=post_id,
        skip=skip,
        limit=limit
    )
    
    # Преобразуем результат в словари
    result = []
    for comment, user_name, post_header in comments:
        comment_dict = comment.__dict__.copy()
        comment_dict["user_name"] = user_name
        comment_dict["post_header"] = post_header
        result.append(comment_dict)
    
    return result


@router.get("/{comment_id}", summary="Получение конкретного комментария")
async def get_comment(
    db: DBDep,
    comment_id: int,
) -> SCommentGet:
    comment = await CommentService(db).get_comment(comment_id)
    if not comment:
        raise CommentNotFoundHTTPError
    return comment


@router.put("/{comment_id}", summary="Обновление комментария")
async def update_comment(
    comment_data: SCommentUpdate,
    db: DBDep,
    current_user: CurrentUserDep,
    comment_id: int,
) -> dict[str, str]:
    try:
        await CommentService(db).update_comment(
            comment_id=comment_id,
            comment_data=comment_data,
            user_id=current_user.id,
            is_admin=getattr(current_user, "is_admin", False)
        )
    except CommentNotFoundError:
        raise CommentNotFoundHTTPError
    except CommentAccessDeniedError:
        raise CommentAccessDeniedHTTPError
    
    return {"status": "OK", "message": "Комментарий успешно обновлен"}


@router.delete("/{comment_id}", summary="Удаление комментария")
async def delete_comment(
    db: DBDep,
    current_user: CurrentUserDep,
    comment_id: int,
) -> dict[str, str]:
    try:
        await CommentService(db).delete_comment(
            comment_id=comment_id,
            user_id=current_user.id,
            is_admin=getattr(current_user, "is_admin", False)
        )
    except CommentNotFoundError:
        raise CommentNotFoundHTTPError
    except CommentAccessDeniedError:
        raise CommentAccessDeniedHTTPError
    
    return {"status": "OK", "message": "Комментарий успешно удален"}


@router.post("/{comment_id}/like", summary="Лайк комментария")
async def like_comment(
    db: DBDep,
    comment_id: int,
) -> dict[str, str]:
    comment = await CommentService(db).get_comment(comment_id)
    if not comment:
        raise CommentNotFoundHTTPError
    
    await CommentService(db).like_comment(comment_id)
    return {"status": "OK", "message": "Лайк добавлен"}


@router.post("/{comment_id}/dislike", summary="Дизлайк комментария")
async def dislike_comment(
    db: DBDep,
    comment_id: int,
) -> dict[str, str]:
    comment = await CommentService(db).get_comment(comment_id)
    if not comment:
        raise CommentNotFoundHTTPError
    
    await CommentService(db).dislike_comment(comment_id)
    return {"status": "OK", "message": "Дизлайк добавлен"}


@router.get("/post/{post_id}/count", summary="Получение количества комментариев к посту")
async def get_comments_count(
    db: DBDep,
    post_id: int,
) -> dict[str, int]:
    count = await CommentService(db).get_comments_count_by_post(post_id)
    return {"post_id": post_id, "comments_count": count}