from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.users import UserModel
from app.repositories.base import BaseRepository
from app.schemes.users import SUserGet, SUserGetWithRelsAndCommunities
from app.schemes.relations_users_roles import SUserGetWithRels


class UsersRepository(BaseRepository):
    model = UserModel
    schema = SUserGet

    async def get_one_or_none_with_role(self, **filter_by):
        query = select(self.model)
        
        for key, value in filter_by.items():
            if hasattr(self.model, key) and value is not None:
                query = query.filter(getattr(self.model, key) == value)
                
        query = query.options(selectinload(self.model.role))

        result = await self.session.execute(query)

        model = result.scalars().one_or_none()
        if model is None:
            return None

        result = SUserGetWithRels.model_validate(model, from_attributes=True)
        return result

    async def get_one_or_none_with_role_and_communities(self, **filter_by):
        query = select(self.model)
        
        for key, value in filter_by.items():
            if hasattr(self.model, key) and value is not None:
                query = query.filter(getattr(self.model, key) == value)
                
        query = query.options(selectinload(self.model.role)).options(selectinload(self.model.communities))

        result = await self.session.execute(query)

        model = result.scalars().one_or_none()
        if model is None:
            return None

        result = SUserGetWithRelsAndCommunities.model_validate(model, from_attributes=True)
        return result

    async def get_recent_users(self, limit: int = 10):
        """Получить последние зарегистрированные пользователи"""
        query = select(self.model).order_by(self.model.id.desc()).limit(limit)
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self.schema.model_validate(model, from_attributes=True) for model in models]
    
    async def get_recent_users_with_role(self, limit: int = 10):
        """Получить последние зарегистрированные пользователи с ролями"""
        query = select(self.model).options(selectinload(self.model.role)).order_by(self.model.id.desc()).limit(limit)
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [SUserGetWithRels.model_validate(model, from_attributes=True) for model in models]
