from typing import TYPE_CHECKING

from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base


class CommentModel(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped [int] = mapped_column(ForeignKey("users.id"), nullable=False)
    post_id: Mapped [int] = mapped_column(ForeignKey("posts.id"), nullable = False)
   
    body: Mapped[str] = mapped_column(String(1500), unique=False, nullable=False)
   
    likes: Mapped[int] = mapped_column()
    dislikes: Mapped[int] = mapped_column()