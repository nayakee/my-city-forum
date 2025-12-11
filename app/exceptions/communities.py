from fastapi import HTTPException, status


class CommunityNotFoundError(Exception):
    """Сообщество не найдено"""
    pass

class CommunityAlreadyExistsError(Exception):
    """Сообщество с таким названием уже существует"""
    pass

class NotCommunityAdminError(Exception):
    """Пользователь не является администратором сообщества"""
    pass

class UserAlreadyInCommunityError(Exception):
    """Пользователь уже состоит в сообществе"""
    pass

class UserNotInCommunityError(Exception):
    """Пользователь не состоит в сообществе"""
    pass


# HTTP исключения
class CommunityNotFoundHTTPError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сообщество не найдено"
        )

class CommunityAlreadyExistsHTTPError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Сообщество с таким названием уже существует"
        )

class NotCommunityAdminHTTPError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав администратора для выполнения этого действия"
        )

class UserAlreadyInCommunityHTTPError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Вы уже состоите в этом сообществе"
        )

class UserNotInCommunityHTTPError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы не состоите в этом сообществе"
        )