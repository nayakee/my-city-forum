from typing import TYPE_CHECKING
import json

from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime, Text
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

    # JSON поле для хранения реакций в SQLite
    reactions_data: Mapped[str] = mapped_column(Text, default='{"liked_by": [], "disliked_by": []}', nullable=True)

    user: Mapped["UserModel"] = relationship(back_populates="comments")
    post: Mapped["PostModel"] = relationship(back_populates="comments")
    
    # Вспомогательные свойства для работы с JSON
    @property
    def reactions_dict(self):
        """Возвращает реакции как словарь Python"""
        try:
            if self.reactions_data:
                return json.loads(self.reactions_data)
        except (json.JSONDecodeError, TypeError):
            pass
        return {"liked_by": [], "disliked_by": []}
    
    @reactions_dict.setter
    def reactions_dict(self, value):
        """Устанавливает реакции из словаря Python"""
        self.reactions_data = json.dumps(value)
    
    def has_user_liked(self, user_id: int) -> bool:
        """Проверяет, лайкал ли пользователь комментарий"""
        reactions = self.reactions_dict
        return user_id in reactions.get("liked_by", [])
    
    def has_user_disliked(self, user_id: int) -> bool:
        """Проверяет, дизлайкал ли пользователь комментарий"""
        reactions = self.reactions_dict
        return user_id in reactions.get("disliked_by", [])
    
    def add_like(self, user_id: int):
        """Добавляет лайк пользователя"""
        reactions = self.reactions_dict
        
        # Убираем из дизлайков если был там
        if user_id in reactions.get("disliked_by", []):
            reactions["disliked_by"].remove(user_id)
            self.dislikes = max(0, (self.dislikes or 0) - 1)
        
        # Добавляем в лайки если еще нет
        if user_id not in reactions.get("liked_by", []):
            reactions["liked_by"].append(user_id)
            self.likes = (self.likes or 0) + 1
        
        self.reactions_dict = reactions
    
    def remove_like(self, user_id: int):
        """Убирает лайк пользователя"""
        reactions = self.reactions_dict
        
        if user_id in reactions.get("liked_by", []):
            reactions["liked_by"].remove(user_id)
            self.likes = max(0, (self.likes or 0) - 1)
            self.reactions_dict = reactions
    
    def add_dislike(self, user_id: int):
        """Добавляет дизлайк пользователя"""
        reactions = self.reactions_dict
        
        # Убираем из лайков если был там
        if user_id in reactions.get("liked_by", []):
            reactions["liked_by"].remove(user_id)
            self.likes = max(0, (self.likes or 0) - 1)
        
        # Добавляем в дизлайки если еще нет
        if user_id not in reactions.get("disliked_by", []):
            reactions["disliked_by"].append(user_id)
            self.dislikes = (self.dislikes or 0) + 1
        
        self.reactions_dict = reactions
    
    def remove_dislike(self, user_id: int):
        """Убирает дизлайк пользователя"""
        reactions = self.reactions_dict
        
        if user_id in reactions.get("disliked_by", []):
            reactions["disliked_by"].remove(user_id)
            self.dislikes = max(0, (self.dislikes or 0) - 1)
            self.reactions_dict = reactions
    
    def get_user_reaction(self, user_id: int) -> str | None:
        """Получает реакцию пользователя ('like', 'dislike' или None)"""
        if self.has_user_liked(user_id):
            return 'like'
        elif self.has_user_disliked(user_id):
            return 'dislike'
        return None

