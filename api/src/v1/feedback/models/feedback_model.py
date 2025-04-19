from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel

from shared.src.tables import FeedbackRating, FeedbackType


class FeedbackCreate(BaseModel):
    """
    Create a new feedback entry.
    """

    type: FeedbackType
    rating: FeedbackRating | None = None
    message: str | None = None
    screen: str
    tags: List[str] | None = None
    app_version: str | None = None
    system_version: str | None = None


class Feedback(FeedbackCreate):
    """
    A feedback entry.
    """

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
