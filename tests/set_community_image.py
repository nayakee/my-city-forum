import asyncio
from app.database.db_manager import DBManager
from app.models.communities import CommunityModel
from sqlalchemy import select

async def set_community_image():
    async with DBManager() as db:
        # Находим сообщество с ID 1
        result = await db.session.execute(select(CommunityModel).filter(CommunityModel.id == 1))
        community = result.scalar_one_or_none()
        
        if community:
            # Устанавливаем путь к изображению
            community.image = "/static/images/icon-theater-masks-5371459.png"
            await db.session.commit()
            print(f"Изображение для сообщества '{community.name}' (ID: {community.id}) установлено на '/static/images/icon-theater-masks-5371459.png'")
        else:
            print("Сообщество с ID 1 не найдено")

if __name__ == "__main__":
    asyncio.run(set_community_image())