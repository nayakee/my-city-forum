from fastapi import HTTPException, status
from app.exceptions.base import MyAppError


class CommentNotFoundError(MyAppError):
    detail = "Комментарий не найден"
    
    def __init__(self, detail=None):
        super().__init__(detail)


class CommentNotFoundHTTPError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Комментарий не найден"
        )


class CommentAccessDeniedError(MyAppError):
    detail = "Нет доступа к комментарию"
    
    def __init__(self, detail=None):
        super().__init__(detail)


class CommentAccessDeniedHTTPError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к комментарию"
        )


class CommentToDeletedPostError(MyAppError):
    detail = "Нельзя добавить комментарий к удаленному посту"
    
    def __init__(self, detail=None):
        super().__init__(detail)


class CommentToDeletedPostHTTPError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя добавить комментарий к удаленному посту"
        )