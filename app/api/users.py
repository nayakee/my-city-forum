from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.api.dependencies import DBDep, get_current_user_id
from app.exceptions.users import UserNotFoundError, UserNotFoundHTTPError
from app.exceptions.roles import RoleNotFoundError
from app.services.users import UserService
from app.services.roles import RoleService
from app.schemes.users import SUserPatch
from app.models.users import UserModel
from app.exceptions.auth import InvalidTokenHTTPError

class AssignRoleRequest(BaseModel):
    role_id: int

router = APIRouter(prefix="/api", tags=["Управление пользователями"])


@router.put("/users/{user_id}/role", summary="Изменение роли пользователя")
async def assign_user_role(
    user_id: int,
    request_data: AssignRoleRequest,
    db: DBDep,
    current_user_id: int = Depends(get_current_user_id)
):
    """Изменение роли пользователя (модераторы и администраторы, модераторы не могут назначать роль администратора)"""
    role_id = request_data.role_id
    
    # Получаем текущего пользователя с ролью для проверки прав
    current_user_service = UserService(db)
    current_user = await current_user_service.get_user_with_role(current_user_id)
    
    # Проверяем права доступа (модератор или администратор)
    if not current_user.role or current_user.role.level < 2:  # 2 - уровень модератора
        raise HTTPException(status_code=403, detail="Недостаточно прав для изменения роли пользователя")
    
    # Если текущий пользователь - модератор (уровень 2), он не может назначать роль администратора (уровень 3)
    target_role = await RoleService(db).get_role(role_id=role_id)
    if current_user.role.level == 2 and target_role.level == 3:
        raise HTTPException(status_code=403, detail="Модератор не может назначать роль администратора")
    
    # Проверяем, что пользователь, которому изменяем роль, существует
    target_user = await UserService(db).get_user(user_id)
    if not target_user:
        raise UserNotFoundHTTPError
    
    # Проверяем, что указанная роль существует
    role_service = RoleService(db)
    try:
        await role_service.get_role(role_id=role_id)
    except RoleNotFoundError:
        raise HTTPException(status_code=400, detail="Указанная роль не существует")
    
    # Изменяем роль пользователя
    try:
        # Используем специальную схему для обновления только роли
        user_update_data = SUserPatch(role_id=role_id)
        await UserService(db).edit_user(user_id, user_update_data)
        await db.commit()
        return {"status": "OK", "message": f"Роль пользователя {user_id} изменена на {role_id}"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при изменении роли: {str(e)}")


class BlockUserRequest(BaseModel):
    reason: str | None = None

@router.post("/users/{user_id}/block", summary="Блокировка пользователя")
async def block_user(
    user_id: int,
    request_data: BlockUserRequest,
    db: DBDep,
    current_user_id: int = Depends(get_current_user_id)
):
    """Блокировка пользователя (только для модераторов и администраторов)"""
    reason = request_data.reason
    
    # Получаем текущего пользователя с ролью для проверки прав
    current_user_service = UserService(db)
    current_user = await current_user_service.get_user_with_role(current_user_id)
    
    # Проверяем права доступа (модератор или администратор)
    if not current_user.role or current_user.role.level < 2:  # 2 - уровень модератора
        raise HTTPException(status_code=403, detail="Недостаточно прав для блокировки пользователя")
    
    # Проверяем, что пользователь, которого блокируем, существует
    target_user = await UserService(db).get_user(user_id)
    if not target_user:
        raise UserNotFoundHTTPError
    
    # Получаем роль "blocked"
    blocked_role = await UserService(db).get_role_by_name("blocked")
    if not blocked_role:
        raise HTTPException(status_code=500, detail="Роль 'blocked' не найдена в системе")
    
    # Изменяем роль пользователя на заблокированную
    try:
        user_update_data = SUserPatch(role_id=blocked_role.id)
        await UserService(db).edit_user(user_id, user_update_data)
        await db.commit()
        return {"status": "OK", "message": f"Пользователь {user_id} заблокирован", "reason": reason or "Не указана"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при блокировке пользователя: {str(e)}")


@router.post("/users/{user_id}/unblock", summary="Разблокировка пользователя")
async def unblock_user(
    user_id: int,
    db: DBDep,
    current_user_id: int = Depends(get_current_user_id)
):
    """Разблокировка пользователя (только для модераторов и администраторов)"""
    
    # Получаем текущего пользователя с ролью для проверки прав
    current_user_service = UserService(db)
    current_user = await current_user_service.get_user_with_role(current_user_id)
    
    # Проверяем права доступа (модератор или администратор)
    if not current_user.role or current_user.role.level < 2:  # 2 - уровень модератора
        raise HTTPException(status_code=403, detail="Недостаточно прав для разблокировки пользователя")
    
    # Проверяем, что пользователь, которого разблокируем, существует
    target_user = await UserService(db).get_user(user_id)
    if not target_user:
        raise UserNotFoundHTTPError
    
    # Получаем роль "user" (обычный пользователь)
    user_role = await UserService(db).get_role_by_name("user")
    if not user_role:
        raise HTTPException(status_code=500, detail="Роль 'user' не найдена в системе")
    
    # Изменяем роль пользователя на обычную
    try:
        user_update_data = SUserPatch(role_id=user_role.id)
        await UserService(db).edit_user(user_id, user_update_data)
        await db.commit()
        return {"status": "OK", "message": f"Пользователь {user_id} разблокирован"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при разблокировке пользователя: {str(e)}")
    