from app.exceptions.base import BaseAppException


class UserNotFoundError(BaseAppException):
    @property
    def message(self) -> str:
        return "Пользователь не найден"


class UserAlreadyExistsError(BaseAppException):
    @property
    def message(self) -> str:
        return "Пользователь с такими данными уже существует"


# HTTP-исключения
class UserNotFoundHTTPError(UserNotFoundError):
    pass


class UserAlreadyExistsHTTPError(UserAlreadyExistsError):
    pass