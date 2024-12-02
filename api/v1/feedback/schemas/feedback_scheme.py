from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import UUID

from shared.tables.feedback_Table import FeedbackRating, FeedbackType

class FeedbackCreate(BaseModel):
    type: FeedbackType
    rating: FeedbackRating = Field(default=FeedbackRating.NEUTRAL)
    message: Optional[str] = None
    screen: str
    tags: Optional[List[str]] = None

class Feedback(FeedbackCreate):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime 