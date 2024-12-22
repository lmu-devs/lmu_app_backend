from typing import Optional
from pydantic import BaseModel

class Rating(BaseModel):
    like_count: int
    is_liked: Optional[bool] = None