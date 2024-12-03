import uuid
from datetime import date, datetime
from typing import List

from pydantic import BaseModel

from api.v1.core import Image
from api.v1.core.schemas.location_scheme import Location
from api.v1.core.schemas.university_scheme import University
from shared.enums.rating_enums import RatingSourceEnum
from shared.enums.university_enums import UniversityEnum


class MovieRating(BaseModel):
    source: RatingSourceEnum
    normalized_rating: float
    raw_rating: str
    
class MovieTrailer(BaseModel):
    id: uuid.UUID
    title: str
    published_at: datetime
    url: str
    thumbnail: Image
    site: str

class Movie(BaseModel):
    id: uuid.UUID
    title: str
    overview: str
    tagline: str
    release_year: date
    budget: int | None
    ratings: List[MovieRating]
    poster: Image
    backdrop: Image
    genres: List[str]
    runtime: int
    homepage: str
    trailers: List[MovieTrailer]
    
class MovieScreening(BaseModel):
    entry_time: datetime
    start_time: datetime
    end_time: datetime
    location: Location
    university: University
    movie: Movie
    
    


