from typing import Optional

from pydantic import BaseModel


class Rating(BaseModel):
    like_count: int
    is_liked: Optional[bool] = None

    @classmethod
    def from_params(cls, like_count: int, is_liked: bool | None = None) -> "Rating":
        return Rating(like_count=like_count, is_liked=is_liked)
