from app.schemes.users import SUserAuth
from pydantic import ValidationError


def test_empty_email_login():
    """Тест валидации пустого email при входе"""
    try:
        SUserAuth(email="", password="password123")
        assert False, "Должна быть выброшена ошибка валидации"
    except ValidationError as e:
        assert "Email не может быть пустым" in str(e) or "Email should not be empty" in str(e)


def test_empty_password_login():
    """Тест валидации пустого пароля при входе"""
    try:
        SUserAuth(email="test@example.com", password="")
        assert False, "Должна быть выброшена ошибка валидации"
    except ValidationError as e:
        assert "Пароль не может быть пустым" in str(e) or "Password should not be empty" in str(e)


def test_invalid_email_format_login():
    """Тест валидации формата email при входе"""
    try:
        SUserAuth(email="invalid_email", password="password123")
        assert False, "Должна быть выброшена ошибка валидации"
    except ValidationError as e:
        assert "Некорректный формат email" in str(e) or "Invalid email format" in str(e)


def test_valid_login_data():
    """Тест валидных данных для входа"""
    user_data = SUserAuth(
        email="test@example.com", 
        password="password123"
    )
    assert user_data.email == "test@example.com"
    assert user_data.password == "password123"


if __name__ == "__main__":
    print("Запуск тестов валидации при входе...")
    
    test_empty_email_login()
    print("Test empty email login passed")
    
    test_empty_password_login()
    print("Test empty password login passed")
    
    test_invalid_email_format_login()
    print("Test invalid email format login passed")
    
    test_valid_login_data()
    print("Test valid login data passed")
    
    print("\nAll login tests passed successfully!")