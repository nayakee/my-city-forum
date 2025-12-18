import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Импортируем все модели, чтобы избежать ошибок связывания
from app.models.users import UserModel  
from app.models.roles import RoleModel
from app.models.communities import CommunityModel
from app.models.comments import CommentModel
from app.models.posts import PostModel
from app.models.reports import ReportModel
from app.models.favorites import FavoriteModel
from app.models.user_communities import UserCommunityModel
from app.models.themes import ThemeModel

from app.database import engine

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