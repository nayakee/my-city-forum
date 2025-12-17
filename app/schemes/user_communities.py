from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SUserCommunityBase(BaseModel):
    user_id: int
    community_id: int


class SUserCommunityCreate(SUserCommunityBase):
    pass


class SUserCommunityUpdate(BaseModel):
    user_id: Optional[int] = None
    community_id: Optional[int] = None


class SUserCommunityGet(SUserCommunityBase):
    id: int
    created_at: datetime
    updated_at: datetime