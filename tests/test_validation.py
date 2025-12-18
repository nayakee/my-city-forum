from app.schemes.users import SUserAddRequest
from pydantic import ValidationError
import pytest


def test_empty_name_validation():
    """Тест валидации пустого имени"""
    try:
        SUserAddRequest(name="", email="test@example.com", password="password123")
        assert False, "Должна быть выброшена ошибка валидации"
    except ValidationError as e:
        assert "Имя не может быть пустым" in str(e) or "Name should not be empty" in str(e)


def test_empty_email_validation():
    """Тест валидации пустого email"""
    try:
        SUserAddRequest(name="Test User", email="", password="password123")
        assert False, "Должна быть выброшена ошибка валидации"
    except ValidationError as e:
        assert "Email не может быть пустым" in str(e) or "Email should not be empty" in str(e)


def test_invalid_email_format():
    """Тест валидации формата email"""
    try:
        SUserAddRequest(name="Test User", email="invalid_email", password="password123")
        assert False, "Должна быть выброшена ошибка валидации"
    except ValidationError as e:
        assert "Некорректный формат email" in str(e) or "Invalid email format" in str(e)


def test_empty_password_validation():
    """Тест валидации пустого пароля"""
    try:
        SUserAddRequest(name="Test User", email="test@example.com", password="")
        assert False, "Должна быть выброшена ошибка валидации"
    except ValidationError as e:
        assert "Пароль не может быть пустым" in str(e) or "Password should not be empty" in str(e)


def test_short_password_validation():
    """Тест валидации короткого пароля"""
    try:
        SUserAddRequest(name="Test User", email="test@example.com", password="123")
        assert False, "Должна быть выброшена ошибка валидации"
    except ValidationError as e:
        assert "не менее 8 символов" in str(e) or "at least 8 characters" in str(e)


def test_long_password_validation():
    """Тест валидации длинного пароля"""
    try:
        long_password = "a" * 51  # 51 символ - больше лимита
        SUserAddRequest(name="Test User", email="test@example.com", password=long_password)
        assert False, "Должна быть выброшена ошибка валидации"
    except ValidationError as e:
        assert "не должен превышать 50 символов" in str(e) or "should not exceed 50 characters" in str(e)


def test_name_length_validation():
    """Тест валидации длины имени"""
    # Тест на имя с длиной больше 35 символов
    try:
        long_name = "a" * 36  # 36 символов - больше лимита
        SUserAddRequest(name=long_name, email="test@example.com", password="password123")
        assert False, "Должна быть выброшена ошибка валидации"
    except ValidationError as e:
        assert "не должно превышать 35 символов" in str(e) or "should not exceed 35 characters" in str(e)


def test_special_chars_in_name():
    """Тест валидации специальных символов в имени"""
    # Тест на имя с недопустимыми символами
    try:
        invalid_name = "John@Doe$"  # содержит специальные символы
        SUserAddRequest(name=invalid_name, email="test@example.com", password="password123")
        assert False, "Должна быть выброшена ошибка валидации"
    except ValidationError as e:
        assert "содержит недопустимые символы" in str(e) or "contains invalid characters" in str(e)


def test_valid_data():
    """Тест валидных данных"""
    user_data = SUserAddRequest(
        name="Test User",
        email="test@example.com",
        password="password123"
    )
    assert user_data.name == "Test User"
    assert user_data.email == "test@example.com"
    assert user_data.password == "password123"


if __name__ == "__main__":
    print("Запуск тестов валидации...")
    
    test_empty_name_validation()
    print("Test empty name passed")
    
    test_empty_email_validation()
    print("Test empty email passed")
    
    test_invalid_email_format()
    print("Test invalid email format passed")
    
    test_empty_password_validation()
    print("Test empty password passed")
    
    test_short_password_validation()
    print("Test short password passed")
    
    test_long_password_validation()
    print("Test long password validation passed")
    
    test_name_length_validation()
    print("Test name length validation passed")
    
    test_special_chars_in_name()
    print("Test special chars in name passed")
    
    test_valid_data()
    print("Test valid data passed")
    
    print("\nAll tests passed successfully!")