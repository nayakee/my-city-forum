from app.exceptions.base import MyAppError, MyAppHTTPError


class RoleNotFoundError(MyAppError):
    detail = "Роли не существует"


class RoleNotFoundHTTPError(MyAppHTTPError):
    status_code = 404
    detail = "Роли не существует"


class RoleAlreadyExistsError(MyAppError):
    detail = "Такая роль уже существует"


class RoleAlreadyExistsHTTPError(MyAppHTTPError):
    status_code = 409
    detail = "Такая роль уже существует"
