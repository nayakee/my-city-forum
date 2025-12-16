from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Path

from app.api.dependencies import DBDep
from app.exceptions.communities import (
    CommunityNotFoundError,
    CommunityNotFoundHTTPError,
    CommunityAlreadyExistsError,
    CommunityAlreadyExistsHTTPError
)
from app.schemes.communities import SCommunityAdd, SCommunityUpdate, SCommunityGet
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
) -> List[SCommunityGet]:
    communities = await CommunitiesService(db).get_communities(
        skip=skip,
        limit=limit,
        search=search
    )
    return communities


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