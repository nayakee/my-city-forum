from typing import TYPE_CHECKING

from pydantic import BaseModel, EmailStr
from datetime import datetime

if TYPE_CHECKING:
    from app.schemes.roles import SRoleGet
    from app.schemes.communities import SCommunityGet


class SUserAddRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role_id: int = 1  # По умолчанию пользовательская роль


class SUserAdd(BaseModel):
    name: str
    email: EmailStr
    hashed_password: str
    role_id: int = 1


class SUserAuth(BaseModel):
    email: EmailStr
    password: str


class SUserGet(SUserAdd):
    id: int
    created_at: datetime | None = None # Добавляем поле даты создания


class SUserPatch(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    hashed_password: str | None = None
    role_id: int | None = None


# Extended user scheme with communities
class SUserGetWithRelsAndCommunities(SUserGet):
    role: 'SRoleGet | None' = None
    communities: list['SCommunityGet'] | None = None

# Rebuild the model to handle forward references properly after all imports are processed
def __rebuild_model__():
    from .roles import SRoleGet
    from .communities import SCommunityGet
    SUserGetWithRelsAndCommunities.model_rebuild()

__rebuild_model__()
