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
    return user


CurrentUserDep = Annotated[SUserGet, Depends(get_current_user)]

# Импортируем необходимые модули для проверки ролей
from app.models.users import UserModel
from app.utils.roles import RoleLevel, check_permissions

# Асинхронная функция для получения пользователя с ролью
async def get_current_user_with_role(db: DBDep = Depends(get_db), user_id: int = Depends(get_current_user_id)) -> UserModel:
    """Получение текущего пользователя с ролью из базы данных"""
    from app.services.users import UserService
    user_service = UserService(db)
    user = await user_service.get_user_with_role(user_id=user_id)
    if not user:
        from app.exceptions.auth import AuthFailedHTTPError
        raise AuthFailedHTTPError
    # Возвращаем объект пользователя с ролью, полученный из UserService
    # который уже включает информацию о роли
    from sqlalchemy.orm import selectinload
    from sqlalchemy import select
    from app.models.users import UserModel
    stmt = select(UserModel).options(selectinload(UserModel.role)).filter(UserModel.id == user.id)
    result = await db.session.execute(stmt)
    user_model = result.scalar_one_or_none()
    if not user_model:
        from app.exceptions.auth import AuthFailedHTTPError
        raise AuthFailedHTTPError
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

# Определяем зависимости FastAPI
AdminDep = Annotated[UserModel, Depends(require_admin)]
ModeratorDep = Annotated[UserModel, Depends(require_moderator)]
UserDepWithRole = Annotated[UserModel, Depends(require_user)]

