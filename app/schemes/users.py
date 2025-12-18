from typing import TYPE_CHECKING

from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime

if TYPE_CHECKING:
    from app.schemes.roles import SRoleGet
    from app.schemes.communities import SCommunityGet


class SUserAddRequest(BaseModel):
    name: str
    email: str  # Изменяем на str, чтобы сначала проверить на пустоту
    password: str
    role_id: int = 1  # По умолчанию пользовательская роль
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or v.strip() == '':
            raise ValueError('Имя не может быть пустым')
        if len(v.strip()) < 1:
            raise ValueError('Имя должно содержать хотя бы один символ')
        if len(v.strip()) > 35:
            raise ValueError('Имя не должно превышать 35 символов')
        # Проверяем, что имя содержит только буквы, цифры, пробелы и дефисы
        import re
        if not re.match(r'^[a-zA-Zа-яА-ЯёЁ0-9\s\-]+$', v.strip()):
            raise ValueError('Имя содержит недопустимые символы')
        return v.strip()
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if not v or v.strip() == '':
            raise ValueError('Email не может быть пустым')
        # Проверяем формат email вручную
        import re
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, v.strip()):
            raise ValueError('Некорректный формат email')
        return v.strip()
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not v or len(v) < 1:
            raise ValueError('Пароль не может быть пустым')
        if len(v) < 8:
            raise ValueError('Пароль должен содержать не менее 8 символов')
        if len(v) > 50:
            raise ValueError('Пароль не должен превышать 50 символов')
        return v


class SUserAdd(BaseModel):
    name: str
    email: EmailStr
    hashed_password: str
    role_id: int = 1


class SUserAuth(BaseModel):
    email: str # Изменяем на str, чтобы проверить на пустоту в валидаторе
    password: str
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if not v or v.strip() == '':
            raise ValueError('Email не может быть пустым')
        # Проверяем формат email вручную
        import re
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, v.strip()):
            raise ValueError('Некорректный формат email')
        return v.strip()
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not v or len(v) < 1:
            raise ValueError('Пароль не может быть пустым')
        return v


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
