from fastapi import HTTPException, status
from app.exceptions.base import MyAppError


class PostNotFoundError(MyAppError):
    detail = "Пост не найден"
    
    def __init__(self, detail=None):
        super().__init__(detail)


class PostNotFoundHTTPError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пост не найден"
        )


class PostAccessDeniedError(Exception):
    pass


class PostAccessDeniedHTTPError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к посту"
        )


class PostAlreadyExistsError(MyAppError):
    detail = "Пост с таким заголовком уже существует"
    
    def __init__(self, detail=None):
        super().__init__(detail)


class PostAlreadyExistsHTTPError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пост с таким заголовком уже существует"
        )