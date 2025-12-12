from fastapi import HTTPException, status


class CommentNotFoundError(Exception):
    pass


class CommentNotFoundHTTPError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Комментарий не найден"
        )


class CommentAccessDeniedError(Exception):
    pass


class CommentAccessDeniedHTTPError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к комментарию"
        )


class CommentToDeletedPostError(Exception):
    pass


class CommentToDeletedPostHTTPError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя добавить комментарий к удаленному посту"
        )