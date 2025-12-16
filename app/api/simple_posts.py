from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from datetime import datetime

from app.api.dependencies import DBDep, CurrentUserDep, UserIdDep, get_current_user_id
from app.schemes.posts import SPostAdd

router = APIRouter(prefix="/api/v2/posts", tags=["Посты v2"])


@router.post("", summary="Создание нового поста")
async def create_post_v2(
    post_data: SPostAdd,
    db: DBDep,
    current_user: int = Depends(get_current_user_id),
):
    """Создание нового поста с использованием модели"""
    try:
        print(f"Создание поста: {post_data.dict()}")
        print(f"Пользователь: {current_user if current_user else 'нет'}")

        if not current_user:
            raise HTTPException(status_code=401, detail="Требуется авторизация")

        # Создаем объект поста с дополнительными полями
        from app.schemes.posts import SPostGet
        # Используем оригинальные данные и добавляем недостающие поля
        post_data_dict = post_data.model_dump()
        post_data_dict.update({
            "user_id": current_user,
            "created_at": datetime.utcnow(),
            "likes": 0,
            "dislikes": 0
        })
        # Обновляем community_id, если он равен 0, то делаем его None
        if post_data_dict["community_id"] == 0:
            post_data_dict["community_id"] = None

        # Альтернативный способ - создание через модель напрямую
        from app.models.posts import PostModel
        new_post = PostModel(
            user_id=post_data_dict["user_id"],
            theme_id=post_data_dict["theme_id"],
            community_id=post_data_dict["community_id"],
            header=post_data_dict["header"],
            body=post_data_dict["body"],
            created_at=post_data_dict["created_at"],
            likes=post_data_dict["likes"],
            dislikes=post_data_dict["dislikes"]
        )
        
        db.session.add(new_post)
        await db.session.commit()
        await db.session.refresh(new_post)
        post_id = new_post.id

        return {
            "status": "OK",
            "message": "Пост успешно создан",
            "post_id": post_id
        }

    except Exception as e:
        await db.session.rollback()
        print(f"Ошибка при создании поста: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка создания поста: {str(e)}")


@router.get("", summary="Получение списка постов")
async def get_posts_v2(
    db: DBDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    theme_id: Optional[int] = None,
):
    """Получение постов с информацией о пользователях и темах"""
    try:
        # Получаем посты с фильтрацией по теме
        posts = await db.posts.get_filtered(
            theme_id=theme_id,
            offset=skip,
            limit=limit
        )

        # Преобразуем в словари и добавляем информацию о пользователях и темах
        posts_list = []
        for post in posts:
            # Получаем информацию о пользователе и теме
            user = await db.users.get(post.user_id)
            theme = await db.themes.get(post.theme_id)

            post_dict = {
                "id": post.id,
                "header": post.header,
                "body": post.body,
                "theme_id": post.theme_id,
                "community_id": post.community_id,
                "user_id": post.user_id,
                "likes": post.likes or 0,
                "dislikes": post.dislikes or 0,
                "created_at": post.created_at,
                "user_name": user.name if user else "Аноним",
                "theme_name": theme.name if theme else "Без темы"
            }
            posts_list.append(post_dict)

        return posts_list

    except Exception as e:
        print(f"Ошибка при получении постов: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/detailed", summary="Получение постов с детальной информацией")
async def get_posts_detailed_v2(
    db: DBDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    theme_id: Optional[int] = None,
):
    """Получение постов с полной информацией"""
    try:
        # Получаем посты с фильтрацией по теме
        posts = await db.posts.get_filtered(
            theme_id=theme_id,
            offset=skip,
            limit=limit
        )

        # Преобразуем в словари и добавляем информацию о пользователях, темах и комментариях
        posts_list = []
        for post in posts:
            # Получаем информацию о пользователе и теме
            user = await db.users.get(post.user_id)
            theme = await db.themes.get(post.theme_id)
            
            # Получаем комментарии к посту для подсчета
            comments = await db.comments.get_filtered(post_id=post.id)

            post_dict = {
                "id": post.id,
                "header": post.header,
                "body": post.body,
                "theme_id": post.theme_id,
                "community_id": post.community_id,
                "user_id": post.user_id,
                "likes": post.likes or 0,
                "dislikes": post.dislikes or 0,
                "created_at": post.created_at,
                "user_name": user.name if user else "Аноним",
                "theme_name": theme.name if theme else "Без темы",
                "comments_count": len(comments)
            }
            posts_list.append(post_dict)

        return posts_list

    except Exception as e:
        print(f"Ошибка при получении детальных постов: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{post_id}/like", summary="Лайк поста")
async def like_post_v2(
    post_id: int,
    db: DBDep,
):
    """Добавление лайка посту"""
    try:
        # Находим пост
        post = await db.posts.get(post_id)

        if not post:
            raise HTTPException(status_code=404, detail="Пост не найден")

        # Обновляем количество лайков
        new_likes = (post.likes or 0) + 1
        await db.posts.edit({"likes": new_likes}, id=post_id)

        return {
            "status": "OK",
            "message": "Лайк добавлен",
            "likes": new_likes
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{post_id}/dislike", summary="Дизлайк поста")
async def dislike_post_v2(
    post_id: int,
    db: DBDep,
):
    """Добавление дизлайка посту"""
    try:
        # Находим пост
        post = await db.posts.get(post_id)

        if not post:
            raise HTTPException(status_code=404, detail="Пост не найден")

        # Обновляем количество дизлайков
        new_dislikes = (post.dislikes or 0) + 1
        await db.posts.edit({"dislikes": new_dislikes}, id=post_id)

        return {
            "status": "OK",
            "message": "Дизлайк добавлен",
            "dislikes": new_dislikes
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))