from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.roles import RoleModel
from app.repositories.base import BaseRepository
from app.schemes.roles import SRoleGet
from app.schemes.relations_users_roles import SRoleGetWithRels


class RolesRepository(BaseRepository):
    model = RoleModel
    schema = SRoleGet

    async def get_one_or_none_with_users(self, **filter_by):
        query = select(self.model)
        
        # Применяем фильтрацию по именованным параметрам
        for key, value in filter_by.items():
            if hasattr(self.model, key) and value is not None:
                query = query.filter(getattr(self.model, key) == value)
                
        query = query.options(selectinload(self.model.users))

        result = await self.session.execute(query)

        model = result.scalars().one_or_none()
        if model is None:
            return None

        result = SRoleGetWithRels.model_validate(model, from_attributes=True)
        return result

    async def check_name_exists_excluding_current(self, name: str, current_role_id: int) -> bool:
        """
        Check if a role name already exists in the database, excluding the current role
        """
        query = select(self.model).filter(
            self.model.name == name,
            self.model.id != current_role_id
        )
        result = await self.session.execute(query)
        existing_role = result.scalars().first()
        return existing_role is not None
