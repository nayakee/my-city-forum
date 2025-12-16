from typing import TYPE_CHECKING

from pydantic import BaseModel, EmailStr

if TYPE_CHECKING:
    from app.schemes.roles import SRoleGet


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


from datetime import datetime

class SUserGet(SUserAdd):
    id: int
    created_at: datetime | None = None # Добавляем поле даты создания


class SUserPatch(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    hashed_password: str | None = None
    role_id: int | None = None
