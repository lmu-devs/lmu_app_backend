from typing import List

from pydantic import BaseModel, RootModel

from shared.src.enums import RatingSourceEnum
from shared.src.tables import MovieRatingTable


class MovieRating(BaseModel):
    source: RatingSourceEnum
    normalized_rating: float
    raw_rating: str

    @classmethod
    def from_table(cls, rating: MovieRatingTable) -> "MovieRating":
        return MovieRating(
            source=rating.source,
            normalized_rating=rating.normalized_value,
            raw_rating=rating.raw_value,
        )


class MovieRatings(RootModel):
    root: List[MovieRating] | list = []

    @classmethod
    def from_table(cls, ratings: List[MovieRatingTable]) -> "MovieRatings":
        ratings = MovieRatings.sort_by_custom_order([MovieRating.from_table(rating) for rating in ratings])
        return MovieRatings(root=ratings)

    @classmethod
    def sort_by_custom_order(cls, ratings: List[MovieRating]) -> List[MovieRating]:
        custom_order = [
            RatingSourceEnum.IMDB,
            RatingSourceEnum.ROTTEN_TOMATOES,
            RatingSourceEnum.METACRITIC,
        ]
        return sorted(ratings, key=lambda x: custom_order.index(x.source))
