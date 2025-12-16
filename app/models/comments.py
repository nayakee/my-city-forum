from typing import TYPE_CHECKING

from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.users import UserModel
    from app.models.posts import PostModel

class CommentModel(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), nullable=False)

    body: Mapped[str] = mapped_column(String(1500), unique=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    likes: Mapped[int] = mapped_column(Integer, default=0, nullable=True)
    dislikes: Mapped[int] = mapped_column(Integer, default=0, nullable=True)

    user: Mapped["UserModel"] = relationship(back_populates="comments")
    post: Mapped["PostModel"] = relationship(back_populates="comments")

