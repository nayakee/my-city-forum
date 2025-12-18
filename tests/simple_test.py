from pydantic import ValidationError
from app.schemes.users import SUserPatch
from app.api.users import AssignRoleRequest

# Тестируем валидацию AssignRoleRequest
print("=== Testing AssignRoleRequest validation ===")

# Правильные данные
try:
    request = AssignRoleRequest(role_id=2)
    print(f"Success: Validation with correct role_id passed: {request}")
except ValidationError as e:
    print(f"Error: Validation with correct role_id failed: {e}")

# Неправильный тип данных
try:
    request = AssignRoleRequest(role_id="invalid")
    print(f"Error: Validation with incorrect type passed (should not happen): {request}")
except ValidationError as e:
    print(f"Success: Validation error with incorrect type data: {e}")

# Отрицательное значение
try:
    request = AssignRoleRequest(role_id=-1)
    print(f"Success: Validation with negative role_id passed: {request}")
except ValidationError as e:
    print(f"Error: Validation error with negative role_id: {e}")

print("\n=== Testing SUserPatch validation ===")

# Правильные данные
try:
    patch = SUserPatch(role_id=2)
    print(f"Success: SUserPatch validation with role_id passed: {patch}")
except ValidationError as e:
    print(f"Error: SUserPatch validation error with role_id: {e}")

# Проверим, что другие поля не обязательны
try:
    patch = SUserPatch()
    print(f"Success: SUserPatch validation without data passed: {patch}")
except ValidationError as e:
    print(f"Error: SUserPatch validation error without data: {e}")