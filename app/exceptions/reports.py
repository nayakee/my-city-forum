from fastapi import HTTPException, status
from app.exceptions.base import MyAppError


class ReportNotFoundError(MyAppError):
    detail = "Жалоба не найдена"
    
    def __init__(self, detail=None):
        super().__init__(detail)


class ReportNotFoundHTTPError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Жалоба не найдена"
        )


class ReportAccessDeniedError(Exception):
    pass


class ReportAccessDeniedHTTPError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к жалобе"
        )


class ContentNotFoundError(MyAppError):
    detail = "Контент не найден"
    
    def __init__(self, detail=None):
        super().__init__(detail)


class ContentNotFoundHTTPError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Контент не найден"
        )


class DuplicateReportError(MyAppError):
    detail = "Вы уже отправляли жалобу на этот контент"
    
    def __init__(self, detail=None):
        super().__init__(detail)


class DuplicateReportHTTPError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Вы уже отправляли жалобу на этот контент"
        )


class OnlyModeratorAccessError(MyAppError):
    detail = "Только модераторы могут выполнять это действие"
    
    def __init__(self, detail=None):
        super().__init__(detail)


class OnlyModeratorAccessHTTPError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только модераторы могут выполнять это действие"
        )