from app.exceptions.base import MyAppError


class UserNotFoundError(MyAppError):
    detail = "Пользователь не найден"
    
    def __init__(self, detail=None):
        super().__init__(detail)


class UserAlreadyExistsError(MyAppError):
    detail = "Пользователь с такими данными уже существует"
    
    def __init__(self, detail=None):
        super().__init__(detail)


# HTTP-исключения
class UserNotFoundHTTPError(UserNotFoundError):
    pass


class UserAlreadyExistsHTTPError(UserAlreadyExistsError):
    pass