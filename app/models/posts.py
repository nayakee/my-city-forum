from typing import TYPE_CHECKING

from datetime import datetime
from sqlalchemy import String, ForeignKey, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.users import UserModel
    from app.models.comments import CommentModel
    from app.models.themes import ThemeModel
    from app.models.communities import CommunityModel

class PostModel(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped [int] = mapped_column(ForeignKey("users.id"), nullable=False)
    theme_id: Mapped [int] = mapped_column(ForeignKey("themes.id"), nullable = False)
    community_id: Mapped[int] = mapped_column(ForeignKey("communities.id"), nullable=True)

    header: Mapped[str] = mapped_column(String(255), unique=False, nullable=False)
    body: Mapped[str] = mapped_column(String(2500), unique=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    likes: Mapped[int] = mapped_column(Integer, default=0, nullable = True)
    dislikes: Mapped[int] = mapped_column(Integer, default=0, nullable = True)

    user: Mapped["UserModel"] = relationship(back_populates="posts")
    theme: Mapped["ThemeModel"] = relationship(back_populates="posts")
    comments: Mapped[list["CommentModel"]] = relationship(back_populates="post", cascade="all, delete-orphan")
    community: Mapped["CommunityModel"] = relationship(back_populates="posts")
