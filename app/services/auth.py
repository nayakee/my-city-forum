from datetime import datetime, timezone, timedelta

from app.config import settings
from app.exceptions.auth import (
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidPasswordError,
    InvalidJWTTokenError,
    JWTTokenExpiredError,
)
from app.exceptions.base import ObjectAlreadyExistsError
from app.schemes.users import (
    SUserAdd,
    SUserAddRequest,
    SUserAuth,
    SUserGetWithRelsAndCommunities
)
from app.schemes.relations_users_roles import SUserGetWithRels
from app.services.base import BaseService
import jwt
from passlib.context import CryptContext
from pydantic import ValidationError


class AuthService(BaseService):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def create_access_token(cls, data: dict) -> str:
        to_encode = data.copy()
        expire: datetime = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode |= {"exp": expire}
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)
        return encoded_jwt

    @classmethod
    def verify_password(cls, plain_password, hashed_password) -> bool:
        return cls.pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def hash_password(cls, plain_password) -> str:
        return cls.pwd_context.hash(plain_password)

    @classmethod
    def decode_token(cls, token: str) -> dict:
        try:
            return jwt.decode(token, settings.SECRET_KEY, [settings.ALGORITHM])
        except jwt.exceptions.DecodeError as ex:
            raise InvalidJWTTokenError from ex
        except jwt.exceptions.ExpiredSignatureError as ex:
            raise JWTTokenExpiredError from ex

    async def register_user(self, user_data: SUserAddRequest):
        try:
            # Проверяем валидность данных пользователя (Pydantic уже делает валидацию)
            hashed_password: str = self.hash_password(user_data.password)
            new_user_data = SUserAdd(
                email=user_data.email,
                hashed_password=hashed_password,
                name=user_data.name,
                role_id=user_data.role_id,
            )
            await self.db.users.add(new_user_data)
        except ObjectAlreadyExistsError:
            raise UserAlreadyExistsError
        except ValidationError as ve:
            # Обработка ошибок валидации Pydantic
            raise ValueError(f"Ошибка валидации: {ve.errors()[0]['msg']}")
        await self.db.commit()

    async def login_user(self, user_data: SUserAuth):
        user = await self.db.users.get_one_or_none_with_role(email=user_data.email)
        if not user:
            raise UserNotFoundError
        if not self.verify_password(user_data.password, user.hashed_password):
            raise InvalidPasswordError
            
        # Проверяем, что пользователь не заблокирован (не имеет роль с level 0)
        if user.role and user.role.level == 0:  # level 0 corresponds to blocked role
            from app.exceptions.auth import InvalidTokenHTTPError
            raise InvalidTokenHTTPError(detail="Ваш аккаунт заблокирован")
            
        # Получаем имя роли, если роль существует
        role_name = user.role.name if user.role else "user" # по умолчанию "user"
        
        access_token: str = self.create_access_token(
            {
                "user_id": user.id,
                "role": role_name,
            }
        )
        return access_token

    async def get_me(self, user_id: int):
        user: SUserGetWithRelsAndCommunities | None = await self.db.users.get_one_or_none_with_role_and_communities(
            id=user_id
        )
        if not user:
            raise UserNotFoundError
            
        # Check if user is blocked (has role with level 0)
        if user.role and user.role.level == 0:
            from app.exceptions.auth import InvalidTokenHTTPError
            raise InvalidTokenHTTPError(detail="Ваш аккаунт заблокирован")
            
        return user
