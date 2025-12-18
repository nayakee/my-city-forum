from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Тестирование эндпоинта изменения роли
def test_assign_role():
    # Простой тест - проверим, что эндпоинт существует
    print("Тестируем эндпоинт изменения роли...")
    
    # Попробуем отправить запрос с неправильными данными, чтобы проверить валидацию
    response = client.put("/api/users/1/role", json={"role_id": "invalid"})
    print(f"Ответ при неправильном типе данных: {response.status_code}")
    print(f"Сообщение об ошибке: {response.json()}")
    
    # Попробуем отправить корректный запрос (хотя пользователь с ID 1 может не существовать)
    response = client.put("/api/users/1/role", json={"role_id": 2})
    print(f"Ответ при корректном типе данных: {response.status_code}")
    print(f"Сообщение: {response.json() if response.content else 'Нет содержимого'}")

if __name__ == "__main__":
    test_assign_role()