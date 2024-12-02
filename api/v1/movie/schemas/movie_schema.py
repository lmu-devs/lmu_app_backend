import uuid
from typing import List
from datetime import datetime
from pydantic import BaseModel

from api.v1.core.schemas.location_scheme import Location
from shared.enums.rating_enums import RatingSource
from api.v1.core import Image


class MovieRating(BaseModel):
    source: RatingSource
    normalized_rating: float
    raw_rating: str
    created_at: datetime
    updated_at: datetime
    
class MovieTrailer(BaseModel):
    id: uuid.UUID
    title: str
    published_at: datetime
    url: str
    thumbnail_url: Image
    site: str

class Movie(BaseModel):
    id: uuid.UUID
    title: str
    overview: str
    tagline: str
    release_year: int
    budget: int | None
    ratings: List[MovieRating]
    poster_url: Image
    backdrop_url: Image
    genres: List[str]
    original_language: str
    runtime: int
    homepage: str
    trailers: List[MovieTrailer]
    
class MovieScreening(BaseModel):
    id: uuid.UUID
    movie: Movie
    entry_time: datetime
    start_time: datetime
    end_time: datetime
    location: Location
    
    


