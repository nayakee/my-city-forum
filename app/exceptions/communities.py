from fastapi import HTTPException, status


class CommunityNotFoundError(Exception):
    pass


class CommunityNotFoundHTTPError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сообщество не найдено"
        )


class CommunityAlreadyExistsError(Exception):
    pass


class CommunityAlreadyExistsHTTPError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Сообщество с таким названием уже существует"
        )