import uuid
from typing import List
from datetime import datetime
from pydantic import BaseModel

from shared.enums.rating_enums import RatingSource
from api.v1.core import Image


class MovieRating(BaseModel):
    source: RatingSource
    normalized_rating: float
    raw_rating: str
    created_at: datetime
    updated_at: datetime

class Movie(BaseModel):
    id: uuid.UUID
    title: str
    year: int
    description: str
    created_at: datetime
    updated_at: datetime
    ratings: List[MovieRating]
    poster_url: Image
    backdrop_url: Image
    genres: List[str]
    original_language: str
    runtime: int
    homepage: str

