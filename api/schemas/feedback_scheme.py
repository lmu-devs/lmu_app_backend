from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID

from shared.models.feedback_model import FeedbackRating

class FeedbackCreate(BaseModel):
    rating: FeedbackRating
    message: Optional[str] = None
    screen: str
    tags: Optional[List[str]] = None

class Feedback(FeedbackCreate):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime 