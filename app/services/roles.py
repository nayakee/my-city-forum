from app.exceptions.base import ObjectAlreadyExistsError
from app.exceptions.roles import RoleNotFoundError, RoleAlreadyExistsError
from app.schemes.roles import SRoleAdd
from app.schemes.relations_users_roles import SRoleGetWithRels
from app.services.base import BaseService


class RoleService(BaseService):

    async def create_role(self, role_data: SRoleAdd):
        try:
            await self.db.roles.add(role_data)
        except ObjectAlreadyExistsError:
            raise RoleAlreadyExistsError
        await self.db.commit()

    async def get_role(self, role_id: int):
        role: SRoleGetWithRels | None = await self.db.roles.get_one_or_none_with_users(
            id=role_id
        )
        if not role:
            raise RoleNotFoundError
        return role

    async def edit_role(self, role_id: int, role_data: SRoleAdd):
        role: SRoleGetWithRels | None = await self.db.roles.get_one_or_none(id=role_id)
        if not role:
            raise RoleNotFoundError
        
        # Check if the new name already exists for another role
        if await self.db.roles.check_name_exists_excluding_current(name=role_data.name, current_role_id=role_id):
            raise RoleAlreadyExistsError
            
        await self.db.roles.edit(role_data, **{"id": role_id})
        await self.db.commit()
        return

    async def delete_role(self, role_id: int):
        role: SRoleGetWithRels | None = await self.db.roles.get_one_or_none(id=role_id)
        if not role:
            raise RoleNotFoundError
        await self.db.roles.delete(id=role_id)
        await self.db.commit()
        return

    async def get_roles(self):
        return await self.db.roles.get_all()
