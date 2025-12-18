from pydantic import ValidationError
from app.schemes.users import SUserPatch

# Проверим, как работает валидация при передаче только role_id
try:
    user_patch = SUserPatch(role_id=2)
    print("Валидация прошла успешно:", user_patch)
    print("role_id:", user_patch.role_id)
    print("email:", user_patch.email)
except ValidationError as e:
    print("Ошибка валидации:", e)
    print("Детали:", e.errors())