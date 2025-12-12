from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SCommentBase(BaseModel):
    body: str
    post_id: int


class SCommentAdd(SCommentBase):
    pass


class SCommentUpdate(BaseModel):
    body: Optional[str] = None


class SCommentGet(SCommentBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    likes: int
    dislikes: int
    created_at: datetime
    
    # Опциональные поля для связей
    user_name: Optional[str] = None
    post_header: Optional[str] = None


class SCommentGetWithReplies(SCommentGet):
    replies_count: int = 0