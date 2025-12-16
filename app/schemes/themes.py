from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class SThemeBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)


class SThemeCreate(SThemeBase):
    pass


class SThemeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)


class SThemeGet(SThemeBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    posts_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class SThemeWithPosts(SThemeGet):
    posts: List[dict] = []


class SThemeStats(BaseModel):
    theme_id: int
    theme_name: str
    total_posts: int
    posts_last_week: int
    posts_last_month: int
    avg_likes: float
    avg_dislikes: float