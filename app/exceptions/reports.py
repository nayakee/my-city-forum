from fastapi import HTTPException, status


class ReportNotFoundError(Exception):
    pass


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


class ContentNotFoundError(Exception):
    pass


class ContentNotFoundHTTPError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Контент не найден"
        )


class DuplicateReportError(Exception):
    pass


class DuplicateReportHTTPError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Вы уже отправляли жалобу на этот контент"
        )


class OnlyModeratorAccessError(Exception):
    pass


class OnlyModeratorAccessHTTPError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только модераторы могут выполнять это действие"
        )