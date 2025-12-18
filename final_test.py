import asyncio
from fastapi.testclient import TestClient
from main import app
from app.database.database import async_session_maker
from app.models.users import UserModel
from app.models.roles import RoleModel
from app.services.auth import AuthService
from sqlalchemy import select
from sqlalchemy.orm import selectinload

def create_test_token(user_id: int) -> str:
    """Создает тестовый токен для пользователя"""
    token_data = {"user_id": user_id}
    token = AuthService.create_access_token(token_data)
    return token

async def setup_test_user():
    """Настраивает тестового пользователя с правами администратора"""
    async with async_session_maker() as session:
        # Найти роль администратора
        result = await session.execute(select(RoleModel).filter(RoleModel.level >= 2))
        admin_role = result.scalars().first()
        
        if not admin_role:
            print("Роль модератора/администратора не найдена")
            return None
        
        # Найти первого пользователя или создать тестового
        result = await session.execute(
            select(UserModel)
            .options(selectinload(UserModel.role))
            .limit(1)
        )
        user = result.scalars().first()
        
        if not user:
            print("Пользователь не найден для теста")
            return None
        
        # Обновить роль пользователя до администратора для теста
        user.role_id = admin_role.id
        session.add(user)
        await session.commit()
        
        return user

def test_endpoint():
    """Проверяет эндпоинт с правильной аутентификацией"""
    client = TestClient(app)
    
    # Настройка тестового пользователя
    user = asyncio.run(setup_test_user())
    
    if not user:
        print("Не удалось настроить тестового пользователя")
        return
    
    print(f"Тестовый пользователь ID {user.id} с ролью {user.role.name} (уровень {user.role.level})")
    
    # Создаем токен для этого пользователя
    token = create_test_token(user.id)
    
    # Найти другого пользователя для изменения роли
    async def get_target_user():
        async with async_session_maker() as session:
            result = await session.execute(
                select(UserModel)
                .filter(UserModel.id != user.id)
                .limit(1)
            )
            target_user = result.scalars().first()
            return target_user.id if target_user else 1  # если нет другого, используем ID 1
    
    target_user_id = asyncio.run(get_target_user())
    
    print(f"Изменяем роль пользователя {target_user_id}")
    
    # Отправляем запрос с правильной аутентификацией
    response = client.put(
        f"/api/users/{target_user_id}/role",
        json={"role_id": 1},  # меняем на роль обычного пользователя
        cookies={"access_token": token}
    )
    
    print(f"Статус ответа: {response.status_code}")
    print(f"Ответ: {response.json() if response.content else 'Нет содержимого'}")
    
    # Проверим случай с несуществующим пользователем
    response_invalid = client.put(
        f"/api/users/9999/role",
        json={"role_id": 1},
        cookies={"access_token": token}
    )
    
    print(f"Статус для несуществующего пользователя: {response_invalid.status_code}")
    print(f"Ответ для несуществующего пользователя: {response_invalid.json() if response_invalid.content else 'Нет содержимого'}")

if __name__ == "__main__":
    test_endpoint()