from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base
import enum

if TYPE_CHECKING:
    from app.models.users import UserModel


# Enum для типов контента
class ReportContentTypeEnum(enum.Enum):
    POST = "post"
    COMMENT = "comment"


# Enum для статусов жалоб
class ReportStatusEnum(enum.Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    RESOLVED = "resolved"
    REJECTED = "rejected"


class ReportModel(Base):
    __tablename__ = "reports"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    reporter_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Тип контента (пост или комментарий)
    content_type: Mapped[ReportContentTypeEnum] = mapped_column(
        Enum(ReportContentTypeEnum),
        nullable=False
    )
    
    # ID контента (поста или комментария)
    content_id: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Причина жалобы
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Дополнительное описание
    description: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Статус жалобы
    status: Mapped[ReportStatusEnum] = mapped_column(
        Enum(ReportStatusEnum),
        default=ReportStatusEnum.PENDING
    )
    
    # Дата создания и обновления
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # ID модератора, который обработал жалобу
    moderator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    
    # Комментарий модератора
    moderator_comment: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Связи
    reporter: Mapped["UserModel"] = relationship(
        "UserModel", 
        foreign_keys=[reporter_id],
        back_populates="reports_made"
    )
    moderator: Mapped["UserModel"] = relationship(
        "UserModel", 
        foreign_keys=[moderator_id],
        back_populates="reports_moderated"
    )
    
    # Свойство для получения связанного контента
    @property
    def content(self):
        """Возвращает связанный пост или комментарий"""
        # Эта связь будет определена динамически в сервисе
        return None