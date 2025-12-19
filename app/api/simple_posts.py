from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from datetime import datetime

from app.api.dependencies import DBDep, CurrentUserDep, UserIdDep, get_current_user_id
from app.schemes.posts import SPostAdd
from app.services.post_reactions import PostReactionService

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
    current_user: int = Depends(get_current_user_id),
):
    """Добавление/удаление лайка посту (один пользователь - один лайк)"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Требуется авторизация")

        # Находим пост
        post = await db.posts.get(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Пост не найден")

        # Используем сервис реакций
        result = await PostReactionService.toggle_reaction(
            db_session=db.session,
            user_id=current_user,
            post_id=post_id,
            reaction_type='like'
        )

        messages = {
            "added": "Лайк добавлен",
            "removed": "Лайк удален",
            "changed": "Дизлайк изменен на лайк"
        }

        return {
            "status": "OK",
            "message": messages[result["action"]],
            "action": result["action"],
            "likes": result["likes"],
            "dislikes": result["dislikes"],
            "user_reaction": result["user_reaction"]
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Ошибка при обработке лайка: {e}")
        await db.session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка обработки лайка: {str(e)}")


@router.post("/{post_id}/dislike", summary="Дизлайк поста")
async def dislike_post_v2(
    post_id: int,
    db: DBDep,
    current_user: int = Depends(get_current_user_id),
):
    """Добавление/удаление дизлайка посту (один пользователь - один дизлайк)"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Требуется авторизация")

        # Находим пост
        post = await db.posts.get(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Пост не найден")

        # Используем сервис реакций
        result = await PostReactionService.toggle_reaction(
            db_session=db.session,
            user_id=current_user,
            post_id=post_id,
            reaction_type='dislike'
        )

        messages = {
            "added": "Дизлайк добавлен",
            "removed": "Дизлайк удален",
            "changed": "Лайк изменен на дизлайк"
        }

        return {
            "status": "OK",
            "message": messages[result["action"]],
            "action": result["action"],
            "likes": result["likes"],
            "dislikes": result["dislikes"],
            "user_reaction": result["user_reaction"]
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Ошибка при обработке дизлайка: {e}")
        await db.session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка обработки дизлайка: {str(e)}")


@router.get("/{post_id}/reaction", summary="Получение реакции пользователя на пост")
async def get_user_reaction(
    post_id: int,
    db: DBDep,
    current_user: int = Depends(get_current_user_id),
):
    """Получает реакцию текущего пользователя на пост"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Требуется авторизация")

        result = await PostReactionService.get_user_reaction(
            db_session=db.session,
            user_id=current_user,
            post_id=post_id
        )

        return {
            "status": "OK",
            "reaction_type": result["reaction_type"],
            "has_liked": result["has_liked"],
            "has_disliked": result["has_disliked"],
            "likes": result["likes"],
            "dislikes": result["dislikes"]
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Ошибка при получении реакции: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения реакции: {str(e)}")


@router.get("/{post_id}/stats", summary="Получение статистики поста")
async def get_post_stats(
    post_id: int,
    db: DBDep,
):
    """Получает статистику лайков/дизлайков поста"""
    try:
        result = await PostReactionService.get_post_stats(
            db_session=db.session,
            post_id=post_id
        )

        return {
            "status": "OK",
            "likes": result["likes"],
            "dislikes": result["dislikes"],
            "total_liked_by": result["total_liked_by"],
            "total_disliked_by": result["total_disliked_by"],
            "total_reactions": result["total_reactions"]
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Ошибка при получении статистики: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения статистики: {str(e)}")


@router.delete("/{post_id}", summary="Удаление поста")
async def delete_post_v2(
    post_id: int,
    db: DBDep,
    current_user: int = Depends(get_current_user_id),
):
    """Удаление поста текущим пользователем или модератором/администратором"""
    try:
        # Находим пост
        post = await db.posts.get(post_id)

        if not post:
            raise HTTPException(status_code=404, detail="Пост не найден")

        # Получаем информацию о текущем пользователе с ролью
        from sqlalchemy.orm import selectinload
        from sqlalchemy import select
        from app.models.users import UserModel
        
        stmt = select(UserModel).options(selectinload(UserModel.role)).filter(UserModel.id == current_user)
        result = await db.session.execute(stmt)
        current_user_info = result.scalar_one_or_none()
        
        if not current_user_info:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        # Проверяем права: владелец поста или модератор/администратор
        is_owner = post.user_id == current_user
        is_moderator_or_admin = hasattr(current_user_info.role, 'level') and current_user_info.role.level >= 2  # предполагаем, что уровень >= 2 - это модератор или админ

        if not (is_owner or is_moderator_or_admin):
            raise HTTPException(status_code=403, detail="Нет прав на удаление этого поста")

        # Удаляем пост
        await db.posts.delete(id=post_id)

        return {
            "status": "OK",
            "message": "Пост успешно удален"
        }

    except HTTPException:
        # Перебрасываем HTTP исключения дальше
        raise
    except Exception as e:
        print(f"Ошибка при удалении поста: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка удаления поста: {str(e)}")


@router.get("/search", summary="Поиск постов")
async def search_posts(
    query: str,
    db: DBDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Поиск постов по заголовку и содержанию"""
    try:
        if len(query.strip()) < 1:
            # Если запрос пустой, возвращаем пустой результат
            return []
            
        # Ищем посты с помощью репозитория
        posts = await db.posts.search(
            search_term=query.strip(),
            skip=skip,
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
            
        print(f"Найдено постов по запросу '{query}': {len(posts_list)}") # Добавим лог для отладки
        return posts_list
        
    except Exception as e:
        print(f"Ошибка при поиске постов: {e}")
        raise HTTPException(status_code=500, detail=str(e))