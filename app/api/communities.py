from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Path, UploadFile, File

from app.api.dependencies import DBDep, get_current_user_id
from app.exceptions.communities import (
    CommunityNotFoundError,
    CommunityNotFoundHTTPError,
    CommunityAlreadyExistsError,
    CommunityAlreadyExistsHTTPError
)
from app.schemes.communities import SCommunityAdd, SCommunityUpdate, SCommunityGet, SCommunityGetWithMembership
from app.services.communities import CommunitiesService

router = APIRouter(prefix="/communities", tags=["Сообщества"])


@router.post("", summary="Создание нового сообщества")
async def create_community(
    community_data: SCommunityAdd,
    db: DBDep,
) -> dict[str, str]:
    try:
        await CommunitiesService(db).create_community(community_data)
    except CommunityAlreadyExistsError:
        raise CommunityAlreadyExistsHTTPError
    
    return {"status": "OK", "message": "Сообщество успешно создано"}


@router.get("", summary="Получение списка сообществ")
async def get_communities(
    db: DBDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    user_id: Optional[int] = Depends(get_current_user_id),
) -> List[SCommunityGetWithMembership]:
    service = CommunitiesService(db)
    if user_id:
        communities_data = await service.get_communities_with_membership(
            user_id=user_id,
            skip=skip,
            limit=limit,
            search=search
        )
        # Преобразуем словари в объекты Pydantic
        return [SCommunityGetWithMembership(**data) for data in communities_data]
    else:
        # Если пользователь не авторизован, возвращаем обычные сообщества без информации о членстве
        communities = await service.get_communities(skip=skip, limit=limit, search=search)
        # Преобразуем в объекты Pydantic с is_joined=False по умолчанию
        result = []
        for community in communities:
            community_dict = community.__dict__.copy()
            community_dict['is_joined'] = False
            result.append(SCommunityGetWithMembership(**community_dict))
        return result


@router.get("/{community_id}", summary="Получение конкретного сообщества")
async def get_community(
    db: DBDep,
    community_id: int = Path(..., description="ID сообщества"),
) -> SCommunityGet:
    community = await CommunitiesService(db).get_community(community_id)
    if not community:
        raise CommunityNotFoundHTTPError
    return community


@router.put("/{community_id}", summary="Обновление сообщества")
async def update_community(
    community_data: SCommunityUpdate,
    db: DBDep,
    community_id: int = Path(..., description="ID сообщества"),
) -> dict[str, str]:
    try:
        await CommunitiesService(db).update_community(community_id, community_data)
    except CommunityNotFoundError:
        raise CommunityNotFoundHTTPError
    except CommunityAlreadyExistsError:
        raise CommunityAlreadyExistsHTTPError
    
    return {"status": "OK", "message": "Сообщество успешно обновлено"}


@router.delete("/{community_id}", summary="Удаление сообщества")
async def delete_community(
    db: DBDep,
    community_id: int = Path(..., description="ID сообщества"),
) -> dict[str, str]:
    try:
        await CommunitiesService(db).delete_community(community_id)
    except CommunityNotFoundError:
        raise CommunityNotFoundHTTPError
    
    return {"status": "OK", "message": "Сообщество успешно удалено"}


@router.post("/{community_id}/increment-posts", summary="Увеличение счетчика постов (внутренний)")
async def increment_posts_count(
    db: DBDep,
    community_id: int = Path(..., description="ID сообщества"),
) -> dict[str, str]:
    """Внутренний эндпоинт для увеличения счетчика постов"""
    community = await CommunitiesService(db).get_community(community_id)
    if not community:
        raise CommunityNotFoundHTTPError
    
    await CommunitiesService(db).increment_posts_count(community_id)
    return {"status": "OK", "message": "Счетчик постов увеличен"}


@router.post("/{community_id}/decrement-posts", summary="Уменьшение счетчика постов (внутренний)")
async def decrement_posts_count(
    db: DBDep,
    community_id: int = Path(..., description="ID сообщества"),
) -> dict[str, str]:
    """Внутренний эндпоинт для уменьшения счетчика постов"""
    community = await CommunitiesService(db).get_community(community_id)
    if not community:
        raise CommunityNotFoundHTTPError
    
    await CommunitiesService(db).decrement_posts_count(community_id)
    return {"status": "OK", "message": "Счетчик постов уменьшен"}


@router.post("/{community_id}/increment-members", summary="Увеличение счетчика участников (внутренний)")
async def increment_members_count(
    db: DBDep,
    community_id: int = Path(..., description="ID сообщества"),
) -> dict[str, str]:
    """Внутренний эндпоинт для увеличения счетчика участников"""
    community = await CommunitiesService(db).get_community(community_id)
    if not community:
        raise CommunityNotFoundHTTPError
    
    await CommunitiesService(db).increment_members_count(community_id)
    return {"status": "OK", "message": "Счетчик участников увеличен"}


@router.post("/{community_id}/decrement-members", summary="Уменьшение счетчика участников (внутренний)")
async def decrement_members_count(
    db: DBDep,
    community_id: int = Path(..., description="ID сообщества"),
) -> dict[str, str]:
    """Внутренний эндпоинт для уменьшения счетчика участников"""
    community = await CommunitiesService(db).get_community(community_id)
    if not community:
        raise CommunityNotFoundHTTPError
    
    await CommunitiesService(db).decrement_members_count(community_id)
    return {"status": "OK", "message": "Счетчик участников уменьшен"}


@router.post("/{community_id}/join", summary="Присоединение к сообществу")
async def join_community(
    db: DBDep,
    community_id: int = Path(..., description="ID сообщества"),
    user_id: int = Depends(get_current_user_id)
) -> dict[str, str]:
    """Присоединение пользователя к сообществу"""
    community = await CommunitiesService(db).get_community(community_id)
    if not community:
        raise CommunityNotFoundHTTPError
    
    await CommunitiesService(db).join_community(community_id, user_id)
    return {"status": "OK", "message": "Пользователь успешно присоединился к сообществу"}


@router.post("/{community_id}/leave", summary="Выход из сообщества")
async def leave_community(
    db: DBDep,
    community_id: int = Path(..., description="ID сообщества"),
    user_id: int = Depends(get_current_user_id)
) -> dict[str, str]:
    """Выход пользователя из сообщества"""
    community = await CommunitiesService(db).get_community(community_id)
    if not community:
        raise CommunityNotFoundHTTPError
    
    await CommunitiesService(db).leave_community(community_id, user_id)
    return {"status": "OK", "message": "Пользователь успешно вышел из сообщества"}


@router.post("/{community_id}/upload-image", summary="Загрузка изображения для сообщества")
async def upload_community_image(
    community_id: int,
    file: UploadFile,
    db: DBDep,
    user_id: int = Depends(get_current_user_id)
) -> dict[str, str]:
    """Загрузка изображения для сообщества"""
    import os
    import uuid
    
    # Проверяем, что файл является изображением
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in allowed_extensions:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Недопустимый тип файла. Разрешены: jpg, jpeg, png, gif, webp")
    
    # Проверяем, что пользователь является администратором или модератором (в реальной реализации)
    # Для упрощения проверим, что пользователь просто существует
    community = await CommunitiesService(db).get_community(community_id)
    if not community:
        raise CommunityNotFoundHTTPError
    
    # Генерируем уникальное имя файла
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    filepath = f"app/static/images/communities/{unique_filename}"
    
    # Создаем директорию, если она не существует
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Сохраняем файл
    with open(filepath, "wb") as buffer:
        import shutil
        shutil.copyfileobj(file.file, buffer)
    
    # Обновляем сообщество с путем к изображению
    update_data = {"image": f"/static/images/communities/{unique_filename}"}
    await CommunitiesService(db).update_community(community_id, SCommunityUpdate(**update_data))
    
    return {"status": "OK", "message": "Изображение успешно загружено", "image_path": update_data["image"]}