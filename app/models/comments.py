from typing import TYPE_CHECKING

from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.users import UserModel
    from app.models.posts import PostModel

class CommentModel(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped [int] = mapped_column(ForeignKey("users.id"), nullable=False)
    post_id: Mapped [int] = mapped_column(ForeignKey("posts.id"), nullable=False)

    body: Mapped[str] = mapped_column(String(1500), unique=False, nullable=False)

    likes: Mapped[int] = mapped_column(default=0)
    dislikes: Mapped[int] = mapped_column(default=0)

    user: Mapped["UserModel"] = relationship(back_populates="comments")
    posts: Mapped["PostModel"] = relationship(back_populates="comments")

