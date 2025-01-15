from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID

from shared.src.tables import FeedbackRating, FeedbackType

class FeedbackCreate(BaseModel):
    type: FeedbackType
    rating: Optional[FeedbackRating] = None
    message: Optional[str] = None
    screen: str
    tags: Optional[List[str]] = None
    app_version: Optional[str] = None
    system_version: Optional[str] = None

class Feedback(FeedbackCreate):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime 