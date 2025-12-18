import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from fastapi.testclient import TestClient
from main import app
from app.database.database import async_session_maker, engine
from app.models.users import UserModel
from app.models.roles import RoleModel
from app.services.auth import AuthService
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import asyncio

client = TestClient(app)

async def get_test_user_and_role():
    """Получить тестового пользователя с ролью администратора"""
    async with async_session_maker() as session:
        # Найти роль администратора
        result = await session.execute(select(RoleModel).filter(RoleModel.level == 3))  # ADMIN
        admin_role = result.scalar_one_or_none()
        
        if not admin_role:
            print("Роль администратора не найдена")
            return None, None
        
        # Найти любого пользователя и обновить его роль до администратора для тестирования
        result = await session.execute(
            select(UserModel)
            .options(selectinload(UserModel.role))
            .limit(1)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print("Пользователь не найден для теста")
            return None, None
        
        # Обновить роль пользователя на администратора для теста
        user.role_id = admin_role.id
        session.add(user)
        await session.commit()
        
        return user, admin_role

def test_role_assignment_with_auth():
    """Тестирование изменения роли с аутентификацией"""
    print("Тестируем изменение роли с аутентификацией...")
    
    # Создаем тестового пользователя-администратора
    async def setup_test_user():
        async with async_session_maker() as session:
            # Найти роль администратора
            result = await session.execute(select(RoleModel).filter(RoleModel.level == 3))
            admin_role = result.scalar_one_or_none()
            
            if not admin_role:
                print("Роль администратора не найдена")
                return None, None
            
            # Найти любого пользователя
            result = await session.execute(
                select(UserModel)
                .options(selectinload(UserModel.role))
                .limit(1)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                print("Пользователь не найден для теста")
                return None, None
            
            # Создаем токен для этого пользователя
            token_data = {"user_id": user.id}
            token = AuthService.create_token(token_data)
            
            return user, token, admin_role.id
    
    # Получаем пользователя и токен
    user, token, admin_role_id = asyncio.run(setup_test_user())
    
    if not user:
        print("Не удалось настроить тестового пользователя")
        return
    
    print(f"Токен создан для пользователя ID {user.id}")
    
    # Пытаемся изменить роль другому пользователю
    # Для этого нужно найти другого пользователя
    async def get_another_user():
        async with async_session_maker() as session:
            result = await session.execute(
                select(UserModel)
                .filter(UserModel.id != user.id)
                .limit(1)
            )
            other_user = result.scalar_one_or_none()
            return other_user.id if other_user else 1  # если нет другого пользователя, используем ID 1
    
    target_user_id = asyncio.run(get_another_user())
    
    # Отправляем запрос с токеном
    response = client.put(
        f"/api/users/{target_user_id}/role",
        json={"role_id": 1},  # меняем на роль пользователя
        cookies={"access_token": token}
    )
    
    print(f"Статус ответа: {response.status_code}")
    print(f"Ответ: {response.json() if response.content else 'Нет содержимого'}")

def test_role_assignment_without_auth():
    """Тестирование изменения роли без аутентификации (ожидаем ошибку)"""
    print("\nТестируем изменение роли без аутентификации...")
    
    response = client.put("/api/users/1/role", json={"role_id": 2})
    print(f"Статус ответа: {response.status_code}")
    print(f"Ответ: {response.json() if response.content else 'Нет содержимого'}")

if __name__ == "__main__":
    test_role_assignment_without_auth()
    test_role_assignment_with_auth()