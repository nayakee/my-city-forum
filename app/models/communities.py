from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.users import UserModel
    from app.models.posts import PostModel

class CommunityModel(Base):
    __tablename__ = "communities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=False, nullable=False)
    description: Mapped[str] = mapped_column(String(255), unique=False, nullable=False)

    posts_count: Mapped[int] = mapped_column(Integer, default=0, nullable = True)
    members_count: Mapped[int] = mapped_column(Integer, default=0, nullable = True)

    users: Mapped[list["UserModel"]] = relationship(secondary="user_communities", back_populates="communities")

    posts: Mapped[list["PostModel"]] = relationship(back_populates="community")