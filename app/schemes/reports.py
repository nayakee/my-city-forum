from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, validator


class ContentType(str, Enum):
    POST = "post"
    COMMENT = "comment"


class ReportStatus(str, Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    RESOLVED = "resolved"
    REJECTED = "rejected"


class SReportCreate(BaseModel):
    content_type: ContentType
    content_id: int
    reason: str = Field(..., min_length=5, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    
    @validator('content_id')
    def content_id_positive(cls, v):
        if v <= 0:
            raise ValueError('ID контента должен быть положительным числом')
        return v


class SReportUpdate(BaseModel):
    status: Optional[ReportStatus] = None
    moderator_comment: Optional[str] = Field(None, max_length=1000)


class SReportGet(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    reporter_id: int
    content_type: ContentType
    content_id: int
    reason: str
    description: Optional[str] = None
    status: ReportStatus
    moderator_id: Optional[int] = None
    moderator_comment: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Дополнительные поля (будут заполнены в сервисе)
    reporter_name: Optional[str] = None
    moderator_name: Optional[str] = None
    content_preview: Optional[str] = None  # заголовок поста или текст комментария
    content_author_id: Optional[int] = None
    content_author_name: Optional[str] = None


class SReportStats(BaseModel):
    total_reports: int
    pending_reports: int
    resolved_reports: int
    rejected_reports: int
    reports_on_posts: int
    reports_on_comments: int