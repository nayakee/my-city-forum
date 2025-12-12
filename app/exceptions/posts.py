from fastapi import HTTPException, status


class PostNotFoundError(Exception):
    pass


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


class PostAlreadyExistsError(Exception):
    pass


class PostAlreadyExistsHTTPError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пост с таким заголовком уже существует"
        )