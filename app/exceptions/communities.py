from fastapi import HTTPException, status
from app.exceptions.base import MyAppError


class CommunityNotFoundError(MyAppError):
    detail = "Сообщество не найдено"
    
    def __init__(self, detail=None):
        super().__init__(detail)


class CommunityNotFoundHTTPError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сообщество не найдено"
        )


class CommunityAlreadyExistsError(MyAppError):
    detail = "Сообщество с таким названием уже существует"
    
    def __init__(self, detail=None):
        super().__init__(detail)


class CommunityAlreadyExistsHTTPError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Сообщество с таким названием уже существует"
        )