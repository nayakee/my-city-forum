from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.roles import RoleModel
    from app.models.communities import CommunityModel


class UserModel(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(300), nullable=False)

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    role: Mapped["RoleModel"] = relationship(back_populates="users")

    reputation: Mapped[int] = mapped_column(Integer, default=0, nullable = True)
    posts_count: Mapped[int] = mapped_column(Integer, default=0, nullable = True)
    comments_count: Mapped[int] = mapped_column(Integer, default=0, nullable = True)
    
    communities: Mapped[list["CommunityModel"]] = relationship(secondary="user_communities", back_populates="users")
 