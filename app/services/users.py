from app.exceptions.base import ObjectAlreadyExistsError
from app.exceptions.users import UserNotFoundError, UserAlreadyExistsError
from app.schemes.users import SUserAdd, SUserGet, SUserPatch
from app.schemes.relations_users_roles import SUserGetWithRels
from app.services.base import BaseService


class UserService(BaseService):
    async def create_user(self, user_data: SUserAdd):
        try:
            await self.db.users.add(user_data)
        except ObjectAlreadyExistsError:
            raise UserAlreadyExistsError
        await self.db.commit()

    async def get_user(self, user_id: int) -> SUserGet:
        user: SUserGet | None = await self.db.users.get_one_or_none(id=user_id)
        if not user:
            raise UserNotFoundError
        return user

    async def get_user_with_role(self, user_id: int) -> SUserGetWithRels:
        user: SUserGetWithRels | None = await self.db.users.get_one_or_none_with_role(id=user_id)
        if not user:
            raise UserNotFoundError
        return user

    async def edit_user(self, user_id: int, user_data: SUserPatch):
        user: SUserGet | None = await self.db.users.get_one_or_none(id=user_id)
        if not user:
            raise UserNotFoundError
        await self.db.users.edit(user_data, exclude_unset=True, id=user_id)
        await self.db.commit()
        return

    async def delete_user(self, user_id: int):
        user: SUserGet | None = await self.db.users.get_one_or_none(id=user_id)
        if not user:
            raise UserNotFoundError
        await self.db.users.delete(id=user_id)
        await self.db.commit()
        return

    async def get_users(self):
        return await self.db.users.get_all()
    
    async def get_recent_users(self, limit: int = 10):
        """Получить последние зарегистрированные пользователи"""
        return await self.db.users.get_recent_users_with_role(limit=limit)
    
    async def get_role_by_name(self, role_name: str):
        """Получить роль по имени"""
        role = await self.db.roles.get_one_or_none(name=role_name)
        return role