from typing import TYPE_CHECKING

from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.users import UserModel


class RoleModel(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 1 - обычный пользователь, 2 - модератор, 3 - администратор

    users: Mapped[list["UserModel"]] = relationship(back_populates="role")
