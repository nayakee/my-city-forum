from typing import Annotated

from fastapi import Depends, Request
from pydantic import BaseModel, Field

from app.database.database import async_session_maker
from app.exceptions.auth import (
    InvalidJWTTokenError,
    InvalidTokenHTTPError,
    NoAccessTokenHTTPError,
    JWTTokenExpiredError,
    JWTTokenExpiredHTTPError
)
from app.schemes.users import SUserGet
from app.services.auth import AuthService
from app.database.db_manager import DBManager


# Удаляем неиспользуемую зависимость PaginationDep, чтобы избежать проблем с кешированием


def get_token(request: Request) -> str:
    token = request.cookies.get("access_token", None)
    if token is None:
        raise NoAccessTokenHTTPError
    return token


def get_current_user_id(token: str = Depends(get_token)) -> int:
    try:
        data = AuthService.decode_token(token)
    except InvalidJWTTokenError:
        raise InvalidTokenHTTPError
    except JWTTokenExpiredError:
        raise JWTTokenExpiredHTTPError
    return data["user_id"]


UserIdDep = Annotated[int, Depends(get_current_user_id)]

async def get_db():
    async with DBManager(session_factory=async_session_maker) as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]

async def get_current_user(user_id: int = Depends(get_current_user_id), db: DBManager = Depends(get_db)) -> SUserGet:
    """Получение текущего пользователя по токену"""
    user = await db.users.get(user_id)
    if not user:
        raise InvalidTokenHTTPError
    
    # Check if user is blocked (has role with level 0)
    if user.role and user.role.level == 0:
        raise InvalidTokenHTTPError(detail="Ваш аккаунт заблокирован")  # Using existing exception with custom message
        
    return user


CurrentUserDep = Annotated[SUserGet, Depends(get_current_user)]

# Импортируем необходимые модули для проверки ролей
from app.models.users import UserModel
from app.utils.roles import RoleLevel, check_permissions

# Асинхронная функция для получения пользователя с ролью
async def get_current_user_with_role(db: DBDep, user_id: int = Depends(get_current_user_id)) -> UserModel:
    """Получение текущего пользователя с ролью из базы данных"""
    from sqlalchemy.orm import selectinload
    from sqlalchemy import select
    
    stmt = select(UserModel).options(selectinload(UserModel.role)).filter(UserModel.id == user_id)
    result = await db.session.execute(stmt)
    user_model = result.scalar_one_or_none()
    
    if not user_model:
        from app.exceptions.auth import InvalidTokenHTTPError
        raise InvalidTokenHTTPError
    
    # Check if user is blocked (has role with level 0)
    if user_model.role and user_model.role.level == 0:
        from app.exceptions.auth import InvalidTokenHTTPError
        raise InvalidTokenHTTPError(detail="Ваш аккаунт заблокирован")  # Using existing exception with custom message
    
    return user_model

async def require_moderator_or_admin(db: DBDep, user_id: int = Depends(get_current_user_id)) -> UserModel:
    """Проверка, что пользователь является модератором или администратором"""
    # Получаем пользователя с ролью напрямую
    from sqlalchemy.orm import selectinload
    from sqlalchemy import select
    
    stmt = select(UserModel).options(selectinload(UserModel.role)).filter(UserModel.id == user_id)
    result = await db.session.execute(stmt)
    user_model = result.scalar_one_or_none()
    
    if not user_model:
        from app.exceptions.auth import InvalidTokenHTTPError
        raise InvalidTokenHTTPError
    
    # Check if user is blocked (has role with level 0)
    if user_model.role and user_model.role.level == 0:
        from app.exceptions.auth import InvalidTokenHTTPError
        raise InvalidTokenHTTPError(detail="Ваш аккаунт заблокирован")  # Using existing exception with custom message
    
    # Проверяем, что пользователь и его роль существуют и уровень роли >= 2
    if not user_model.role or user_model.role.level < 2:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=403,
            detail=f"Недостаточно прав. Требуется уровень MODERATOR или ADMIN"
        )
    
    return user_model
# Функции-зависимости для проверки уровней доступа
async def require_admin(current_user: UserModel = Depends(get_current_user_with_role)) -> UserModel:
    from app.utils.roles import RoleLevel, check_permissions
    permission_checker = check_permissions(RoleLevel.ADMIN)
    return permission_checker(current_user)

async def require_moderator(current_user: UserModel = Depends(get_current_user_with_role)) -> UserModel:
    from app.utils.roles import RoleLevel, check_permissions
    permission_checker = check_permissions(RoleLevel.MODERATOR)
    return permission_checker(current_user)
async def require_user(current_user: UserModel = Depends(get_current_user_with_role)) -> UserModel:
    from app.utils.roles import RoleLevel, check_permissions
    permission_checker = check_permissions(RoleLevel.USER)
    return permission_checker(current_user)

async def require_moderator_or_admin(current_user: UserModel = Depends(get_current_user_with_role)) -> UserModel:
    """Проверка, что пользователь является модератором или администратором"""
    if current_user.role.level < RoleLevel.MODERATOR:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=403,
            detail=f"Недостаточно прав. Требуется уровень MODERATOR или ADMIN"
        )
    return current_user

# Определяем зависимости FastAPI
AdminDep = Annotated[UserModel, Depends(require_admin)]
ModeratorDep = Annotated[UserModel, Depends(require_moderator)]
UserDepWithRole = Annotated[UserModel, Depends(require_user)]
ModeratorOrAdminDep = Annotated[UserModel, Depends(require_moderator_or_admin)]


