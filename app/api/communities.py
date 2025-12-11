from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.api.dependencies import DBDep, UserIdDep
from app.services.communities import CommunitiesService
from app.exceptions.communities import (
    CommunityNotFoundHTTPError,
    CommunityAlreadyExistsHTTPError,
    UserAlreadyInCommunityHTTPError,
    UserNotInCommunityHTTPError,
)

# Схемы Pydantic для пользователей
class SCommunity(BaseModel):
    id: int
    name: str
    description: str
    members_count: int = 0
    posts_count: int = 0
    
    class Config:
        from_attributes = True

class SCommunityMember(BaseModel):
    user_id: int
    community_id: int
    joined_at: datetime
    username: str
    
    class Config:
        from_attributes = True

class SUserCommunity(BaseModel):
    community_id: int
    community_name: str
    joined_at: datetime
    members_count: int
    posts_count: int

# Схемы Pydantic для админов
class SCommunityCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description="Название сообщества")
    description: str = Field(..., min_length=10, max_length=500, description="Описание сообщества")

class SCommunityUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100, description="Название сообщества")
    description: Optional[str] = Field(None, min_length=10, max_length=500, description="Описание сообщества")

class SCommunityStats(BaseModel):
    total_communities: int
    total_members: int
    total_posts: int
    top_communities: List[dict]

router = APIRouter(prefix="/communities", tags=["Сообщества"])


# ============ РУЧКИ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ ============

@router.get("/", summary="Получить список всех сообществ")
async def get_all_communities(
    db: DBDep,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> List[SCommunity]:
    """
    Получение списка сообществ с возможностью поиска.
    """
    communities = await CommunitiesService(db).get_communities(search, skip, limit)
    
    return [
        SCommunity.from_attr(community) for community in communities
    ]


@router.get("/{community_id}", summary="Получить информацию о сообществе")
async def get_community(
    db: DBDep,
    community_id: int,
) -> SCommunity:
    """
    Получение информации о сообществе.
    """
    try:
        community = await CommunitiesService(db).get_community_by_id(community_id)
    except Exception as e:
        raise CommunityNotFoundHTTPError()
    
    return SCommunity.from_attr(community)


@router.post("/{community_id}/join", summary="Присоединиться к сообществу")
async def join_community(
    db: DBDep,
    user_id: UserIdDep,
    community_id: int,
) -> dict[str, str]:
    """
    Присоединение пользователя к сообществу.
    """
    try:
        await CommunitiesService(db).join_community(user_id, community_id)
    except Exception as e:
        if "CommunityNotFound" in str(e.__class__.__name__):
            raise CommunityNotFoundHTTPError()
        elif "UserAlreadyInCommunity" in str(e.__class__.__name__):
            raise UserAlreadyInCommunityHTTPError()
        raise HTTPException(status_code=500, detail="Ошибка сервера")
    
    return {"status": "OK", "message": "Вы присоединились к сообществу"}


@router.post("/{community_id}/leave", summary="Покинуть сообщество")
async def leave_community(
    db: DBDep,
    user_id: UserIdDep,
    community_id: int,
) -> dict[str, str]:
    """
    Выход пользователя из сообщества.
    """
    try:
        await CommunitiesService(db).leave_community(user_id, community_id)
    except Exception as e:
        if "CommunityNotFound" in str(e.__class__.__name__):
            raise CommunityNotFoundHTTPError()
        elif "UserNotInCommunity" in str(e.__class__.__name__):
            raise UserNotInCommunityHTTPError()
        raise HTTPException(status_code=500, detail="Ошибка сервера")
    
    return {"status": "OK", "message": "Вы покинули сообщество"}


@router.get("/user/me", summary="Получить сообщества текущего пользователя")
async def get_user_communities(
    db: DBDep,
    user_id: UserIdDep,
) -> List[SUserCommunity]:
    """
    Получение списка сообществ, в которых состоит текущий пользователь.
    """
    user_communities = await CommunitiesService(db).get_user_communities(user_id)
    
    return [
        SUserCommunity(
            community_id=uc.CommunityModel.id,
            community_name=uc.CommunityModel.name,
            joined_at=uc.joined_at,
            members_count=uc.CommunityModel.members_count,
            posts_count=uc.CommunityModel.posts_count
        )
        for uc in user_communities
    ]


@router.get("/{community_id}/members", summary="Получить список участников сообщества")
async def get_community_members(
    db: DBDep,
    community_id: int,
    skip: int = 0,
    limit: int = 50,
) -> List[SCommunityMember]:
    """
    Получение списка участников сообщества с пагинацией.
    """
    try:
        members = await CommunitiesService(db).get_community_members(community_id, skip, limit)
    except Exception as e:
        if "CommunityNotFound" in str(e.__class__.__name__):
            raise CommunityNotFoundHTTPError()
        raise HTTPException(status_code=500, detail="Ошибка сервера")
    
    return [
        SCommunityMember(
            user_id=member.UserCommunityModel.user_id,
            community_id=member.UserCommunityModel.community_id,
            joined_at=member.UserCommunityModel.joined_at,
            username=member.username
        )
        for member in members
    ]


@router.get("/{community_id}/check", summary="Проверить состоит ли пользователь в сообществе")
async def check_community_membership(
    db: DBDep,
    user_id: UserIdDep,
    community_id: int,
) -> dict[str, bool]:
    """
    Проверка, состоит ли текущий пользователь в сообществе.
    """
    try:
        await CommunitiesService(db).get_community_by_id(community_id)
    except Exception as e:
        if "CommunityNotFound" in str(e.__class__.__name__):
            raise CommunityNotFoundHTTPError()
        raise HTTPException(status_code=500, detail="Ошибка сервера")
    
    is_member = await CommunitiesService(db).is_user_in_community(user_id, community_id)
    
    return {"is_member": is_member}


# ============ АДМИНСКИЕ РУЧКИ ============

@router.post("/admin/create", summary="Создать новое сообщество (только для администраторов)")
async def admin_create_community(
    db: DBDep,
    user_id: UserIdDep,
    community_data: SCommunityCreate,
) -> dict[str, str]:
    """
    Создание нового сообщества.
    Только для администраторов системы.
    """
    try:
        await CommunitiesService(db).create_community(
            user_id, 
            community_data.name, 
            community_data.description
        )
    except Exception as e:
        if "CommunityAlreadyExists" in str(e.__class__.__name__):
            raise CommunityAlreadyExistsHTTPError()
        raise HTTPException(status_code=500, detail="Ошибка сервера")
    
    return {"status": "OK", "message": "Сообщество успешно создано"}


@router.put("/admin/{community_id}", summary="Обновить информацию о сообществе (только для администраторов)")
async def admin_update_community(
    db: DBDep,
    user_id: UserIdDep,
    community_id: int,
    community_data: SCommunityUpdate,
) -> dict[str, str]:
    """
    Обновление информации о сообществе.
    Только для администраторов системы.
    """
    try:
        await CommunitiesService(db).update_community(
            user_id, 
            community_id, 
            name=community_data.name,
            description=community_data.description
        )
    except Exception as e:
        if "CommunityNotFound" in str(e.__class__.__name__):
            raise CommunityNotFoundHTTPError()
        elif "CommunityAlreadyExists" in str(e.__class__.__name__):
            raise CommunityAlreadyExistsHTTPError()
        raise HTTPException(status_code=500, detail="Ошибка сервера")
    
    return {"status": "OK", "message": "Информация о сообществе обновлена"}


@router.delete("/admin/{community_id}", summary="Удалить сообщество (только для администраторов)")
async def admin_delete_community(
    db: DBDep,
    user_id: UserIdDep,
    community_id: int,
) -> dict[str, str]:
    """
    Удаление сообщества.
    Только для администраторов системы.
    """
    try:
        await CommunitiesService(db).delete_community(user_id, community_id)
    except Exception as e:
        if "CommunityNotFound" in str(e.__class__.__name__):
            raise CommunityNotFoundHTTPError()
        raise HTTPException(status_code=500, detail="Ошибка сервера")
    
    return {"status": "OK", "message": "Сообщество удалено"}


@router.get("/admin/statistics", summary="Получить статистику по сообществам (только для администраторов)")
async def admin_get_statistics(
    db: DBDep,
    user_id: UserIdDep,
) -> SCommunityStats:
    """
    Получение статистики по сообществам.
    Только для администраторов системы.
    """
    try:
        stats = await CommunitiesService(db).get_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка сервера")
    
    return SCommunityStats(**stats)


@router.get("/admin/list", summary="Получить полный список сообществ (только для администраторов)")
async def admin_get_all_communities(
    db: DBDep,
    user_id: UserIdDep,
    skip: int = 0,
    limit: int = 100,
) -> List[SCommunity]:
    """
    Получение полного списка сообществ с пагинацией.
    Только для администраторов системы.
    """
    communities = await CommunitiesService(db).get_communities(None, skip, limit)
    
    return [
        SCommunity.from_attr(community) for community in communities
    ]