from typing import List
from pydantic import BaseModel

from shared.src.tables import MovieRatingTable
from shared.src.enums import RatingSourceEnum

class MovieRating(BaseModel):
    source: RatingSourceEnum
    normalized_rating: float
    raw_rating: str
    
    @classmethod
    def from_table(cls, rating: MovieRatingTable) -> 'MovieRating':
        return MovieRating(
            source=rating.source,
            normalized_rating=rating.normalized_value,
            raw_rating=rating.raw_value,
        )

        
class MovieRatings(BaseModel):
    ratings: List[MovieRating]
    
    @classmethod
    def from_table(cls, ratings: List[MovieRatingTable]) -> 'MovieRatings':
        return MovieRatings(ratings=[MovieRating.from_table(rating) for rating in ratings])
