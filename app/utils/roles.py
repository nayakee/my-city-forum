from enum import IntEnum
from fastapi import HTTPException, Depends
from app.models.users import UserModel


class RoleLevel(IntEnum):
    """
    Уровни доступа пользователей:
    USER - обычный пользователь (уровень 1)
    MODERATOR - модератор (уровень 2)
    ADMIN - администратор (уровень 3)
    """
    USER = 1
    MODERATOR = 2
    ADMIN = 3


def check_permissions(required_level: RoleLevel):
    """
    Декоратор для проверки уровня доступа пользователя
    """
    def permission_checker(current_user: UserModel) -> UserModel:
        if current_user.role.level < required_level:
            raise HTTPException(
                status_code=403,
                detail=f"Недостаточно прав. Требуется уровень {required_level.name}"
            )
        return current_user
    return permission_checker


def is_admin(user: UserModel) -> bool:
    """Проверяет, является ли пользователь администратором"""
    return user.role.level >= RoleLevel.ADMIN


def is_moderator(user: UserModel) -> bool:
    """Проверяет, является ли пользователь модератором или выше"""
    return user.role.level >= RoleLevel.MODERATOR


def is_user(user: UserModel) -> bool:
    """Проверяет, является ли пользователь обычным пользователем или выше"""
    return user.role.level >= RoleLevel.USER