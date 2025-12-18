from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SPostBase(BaseModel):
    header: str
    body: str
    theme_id: int
    community_id: Optional[int] = None


class SPostAdd(SPostBase):
    pass


class SPostUpdate(BaseModel):
    header: Optional[str] = None
    body: Optional[str] = None
    theme_id: Optional[int] = None
    community_id: Optional[int] = None


class SPostGet(SPostBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    likes: int
    dislikes: int
    created_at: datetime
    
    # Опциональные поля для связей
    user_name: Optional[str] = None
    theme_name: Optional[str] = None
    community_name: Optional[str] = None


class SPostGetWithComments(SPostGet):
    comments_count: int = 0

class PostReactionResponse(BaseModel):
    status: str
    message: str
    action: str
    likes: int
    dislikes: int
    user_reaction: Optional[str] = None

class UserReactionResponse(BaseModel):
    status: str
    reaction_type: Optional[str]
    has_liked: bool
    has_disliked: bool
    likes: int
    dislikes: int

class PostStatsResponse(BaseModel):
    status: str
    likes: int
    dislikes: int
    total_liked_by: int
    total_disliked_by: int
    total_reactions: int