import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Импортируем только нужные модели
from app.models.roles import RoleModel
from app.models.users import UserModel

from app.database.database import engine

async def check_roles():
    async with AsyncSession(engine) as session:
        result = await session.execute(select(RoleModel))
        roles = result.scalars().all()
        print('Existing roles:')
        for r in roles:
            print(f'ID: {r.id}, Name: {r.name}, Level: {r.level}')
        return roles

if __name__ == "__main__":
    asyncio.run(check_roles())