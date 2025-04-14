from enum import Enum

from pydantic import BaseModel, RootModel

from api.src.v1.cinema.models.movie_screening_model import MovieScreenings
from shared.src.enums.home_tile_enums import HomeTileEnum
from shared.src.enums.language_enums import LanguageEnum


class HomeTileTranslation(BaseModel):
    language: LanguageEnum
    title: str
    description: str


class HomeTile(BaseModel):
    __abstract__ = True
    type: HomeTileEnum
    size: int
    translations: list[HomeTileTranslation]


class MovieHomeTile(HomeTile):
    type: HomeTileEnum = HomeTileEnum.CINEMAS
    screenings: MovieScreenings
