from fastapi import HTTPException


class MyAppError(Exception):
    detail = "Неожиданная ошибка"

    def __init__(self, detail=None):
        message = detail if detail is not None else self.detail
        super().__init__(message)


class MyAppHTTPError(HTTPException):
    status_code = 500
    detail = "Неожиданная ошибка"

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class ObjectNotFoundError(MyAppError):
    detail = "Объект не найден"
    
    def __init__(self, detail=None):
        super().__init__(detail)


class ObjectAlreadyExistsError(MyAppError):
    detail = "Похожий объект уже существует"
    
    def __init__(self, detail=None):
        super().__init__(detail)


class InvalidDateRangeError(MyAppError):
    detail = "Дата заезда не может быть позже даты выезда"
    
    def __init__(self, detail=None):
        super().__init__(detail)
