from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class SCommunityBase(BaseModel):
    name: str
    description: str


class SCommunityAdd(SCommunityBase):
    pass


class SCommunityUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class SCommunityGet(SCommunityBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    posts_count: int
    members_count: int