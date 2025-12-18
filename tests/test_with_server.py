import asyncio
from fastapi.testclient import TestClient
from main import app
from app.database.database import async_session_maker
from app.models.users import UserModel
from app.models.roles import RoleModel
from app.services.auth import AuthService
from sqlalchemy import select
from sqlalchemy.orm import selectinload

def test_with_auth():
    """Тестирование эндпоинта с аутентификацией"""
    client = TestClient(app)
    
    # Получить токен аутентифицированного пользователя с правами модератора/администратора
    async def get_auth_token():
        async with async_session_maker() as session:
            # Найти роль администратора
            result = await session.execute(select(RoleModel).filter(RoleModel.level >= 2))  # MODERATOR или ADMIN
            admin_role = result.scalars().first()
            
            if not admin_role:
                print("Роль модератора/администратора не найдена")
                return None, None
            
            # Найти пользователя с этой ролью или первого пользователя и обновить его роль
            result = await session.execute(
                select(UserModel)
                .options(selectinload(UserModel.role))
                .limit(1)
            )
            user = result.scalars().first()
            
            if not user:
                print("Пользователь не найден для теста")
                return None, None
            
            # Обновить роль пользователя до модератора/администратора для теста
            user.role_id = admin_role.id
            session.add(user)
            await session.commit()
            
            # Создаем токен для этого пользователя
            token_data = {"user_id": user.id}
            token = AuthService.create_access_token(token_data)
            
            return user.id, token
    
    user_id, token = asyncio.run(get_auth_token())
    
    if not token:
        print("Не удалось получить токен для теста")
        return
    
    print(f"Токен получен для пользователя ID {user_id}")
    
    # Найти другого пользователя для теста изменения роли
    async def get_target_user():
        async with async_session_maker() as session:
            result = await session.execute(
                select(UserModel)
                .filter(UserModel.id != user_id)
                .limit(1)
            )
            user = result.scalars().first()
            return user.id if user else 1 # если нет другого пользователя, используем ID 1
    
    target_user_id = asyncio.run(get_target_user())
    
    # Отправляем запрос с правильной аутентификацией
    response = client.put(
        f"/api/users/{target_user_id}/role",
        json={"role_id": 1},  # меняем на роль обычного пользователя
        cookies={"access_token": token}
    )
    
    print(f"Статус ответа: {response.status_code}")
    print(f"Ответ: {response.json() if response.content else 'Нет содержимого'}")
    
    # Проверим также случай с несуществующей ролью
    response_invalid = client.put(
        f"/api/users/{target_user_id}/role",
        json={"role_id": 999},  # несуществующая роль
        cookies={"access_token": token}
    )
    
    print(f"Статус ответа для несуществующей роли: {response_invalid.status_code}")
    print(f"Ответ для несуществующей роли: {response_invalid.json() if response_invalid.content else 'Нет содержимого'}")

if __name__ == "__main__":
    test_with_auth()