from typing import Optional
from pydantic import BaseModel


class RatingDto(BaseModel):
    like_count: int
    is_liked: Optional[bool] = None