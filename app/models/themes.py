from typing import TYPE_CHECKING

from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.posts import PostModel


class ThemeModel(Base):
    __tablename__ = "themes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    posts_count: Mapped[int] = mapped_column(Integer, default=0, nullable=True)

    posts: Mapped[list["PostModel"]] = relationship(back_populates="theme", cascade="all, delete-orphan")