from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from app.schemes.users import SUserGet


class SRoleAdd(BaseModel):
    name: str
    level: int = 1  # 1 - обычный пользователь, 2 - модератор, 3 - администратор


class SRoleGet(SRoleAdd):
    id: int
