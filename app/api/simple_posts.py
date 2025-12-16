from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import insert, select
from datetime import datetime

from app.api.dependencies import DBDep, CurrentUserDep
from app.schemes.posts import SPostAdd
from app.models.posts import PostModel
from app.models.users import UserModel
from app.models.themes import ThemeModel
from app.models.communities import CommunityModel
from sqlalchemy.orm import selectinload, joinedload

router = APIRouter(prefix="/api/v2/posts", tags=["Посты v2"])


@router.post("", summary="Создание нового поста")
async def create_post_v2(
    post_data: SPostAdd,
    db: DBDep,
    current_user = Depends(CurrentUserDep),
):
    """Создание нового поста с использованием модели"""
    try:
        print(f"Создание поста: {post_data.dict()}")
        print(f"Пользователь: {current_user.id if current_user else 'нет'}")

        if not current_user:
            raise HTTPException(status_code=401, detail="Требуется авторизация")

        # Создаем пост
        post_values = {
            "user_id": current_user.id,
            "theme_id": post_data.theme_id,
            "community_id": post_data.community_id,
            "header": post_data.header,
            "body": post_data.body,
            "created_at": datetime.utcnow(),
            "likes": 0,
            "dislikes": 0
        }

        # Вставляем пост в базу
        stmt = insert(PostModel).values(**post_values).returning(PostModel.id)
        result = await db.database.execute(stmt)
        post_id = result

        return {
            "status": "OK",
            "message": "Пост успешно создан",
            "post_id": post_id
        }

    except Exception as e:
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
        # Базовый запрос
        query = (
            select(PostModel)
            .join(UserModel, PostModel.user_id == UserModel.id)
            .join(ThemeModel, PostModel.theme_id == ThemeModel.id)
            .options(
                selectinload(PostModel.user),
                selectinload(PostModel.theme)
            )
            .order_by(PostModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        # Фильтрация по теме
        if theme_id:
            query = query.where(PostModel.theme_id == theme_id)

        # Выполняем запрос
        result = await db.database.execute(query)
        posts = result.scalars().all()

        # Преобразуем в словари
        posts_list = []
        for post in posts:
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
                "user_name": post.user.name if post.user else "Аноним",
                "theme_name": post.theme.name if post.theme else "Без темы"
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
        # Базовый запрос с подсчетом комментариев
        from sqlalchemy import func
        from app.models.comments import CommentModel
        
        query = (
            select(
                PostModel,
                UserModel.name.label("user_name"),
                ThemeModel.name.label("theme_name"),
                func.count(CommentModel.id).label("comments_count")
            )
            .join(UserModel, PostModel.user_id == UserModel.id)
            .join(ThemeModel, PostModel.theme_id == ThemeModel.id)
            .outerjoin(CommentModel, PostModel.id == CommentModel.post_id)
            .group_by(PostModel.id, UserModel.name, ThemeModel.name)
            .order_by(PostModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        # Фильтрация по теме
        if theme_id:
            query = query.where(PostModel.theme_id == theme_id)

        # Выполняем запрос
        result = await db.database.execute(query)
        rows = result.all()

        # Преобразуем в словари
        posts_list = []
        for row in rows:
            post, user_name, theme_name, comments_count = row
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
                "user_name": user_name or "Аноним",
                "theme_name": theme_name or "Без темы",
                "comments_count": comments_count or 0
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
        stmt = select(PostModel).where(PostModel.id == post_id)
        result = await db.database.execute(stmt)
        post = result.scalar_one_or_none()

        if not post:
            raise HTTPException(status_code=404, detail="Пост не найден")

        # Обновляем количество лайков
        new_likes = (post.likes or 0) + 1
        update_stmt = (
            db.posts.update()
            .where(db.posts.c.id == post_id)
            .values(likes=new_likes)
        )
        await db.database.execute(update_stmt)

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
        stmt = select(PostModel).where(PostModel.id == post_id)
        result = await db.database.execute(stmt)
        post = result.scalar_one_or_none()

        if not post:
            raise HTTPException(status_code=404, detail="Пост не найден")

        # Обновляем количество дизлайков
        new_dislikes = (post.dislikes or 0) + 1
        update_stmt = (
            db.posts.update()
            .where(db.posts.c.id == post_id)
            .values(dislikes=new_dislikes)
        )
        await db.database.execute(update_stmt)

        return {
            "status": "OK",
            "message": "Дизлайк добавлен",
            "dislikes": new_dislikes
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))