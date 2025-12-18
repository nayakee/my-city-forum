from fastapi.testclient import TestClient
from main import app
import jwt
from app.config import settings

client = TestClient(app)

def test_endpoint_without_auth():
    """Тестируем эндпоинт без аутентификации"""
    print("Тестирование эндпоинта без аутентификации...")
    
    # Отправляем запрос без токена
    response = client.put("/api/users/1/role", json={"role_id": 2})
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.json()}")
    
def test_endpoint_with_invalid_auth():
    """Тестируем эндпоинт с невалидным токеном"""
    print("\nТестирование эндпоинта с невалидным токеном...")
    
    # Отправляем запрос с невалидным токеном
    response = client.put(
        "/api/users/1/role", 
        json={"role_id": 2},
        cookies={"access_token": "invalid_token_here"}
    )
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.json()}")
    
def test_endpoint_with_valid_structure_token():
    """Тестируем эндпоинт с токеном правильной структуры, но возможно невалидным"""
    print("\nТестирование эндпоинта с токеном правильной структуры...")
    
    # Создаем поддельный токен с правильной структурой
    fake_payload = {"user_id": 1}
    fake_token = jwt.encode(fake_payload, "wrong_secret", algorithm="HS256")
    
    response = client.put(
        "/api/users/1/role", 
        json={"role_id": 2},
        cookies={"access_token": fake_token}
    )
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.json()}")

if __name__ == "__main__":
    test_endpoint_without_auth()
    test_endpoint_with_invalid_auth()
    test_endpoint_with_valid_structure_token()