from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, Field, RootModel

from api.src.v1.cinema.models.movie_screening_model import MovieScreenings
from shared.src.enums.home_tile_enums import HomeTileEnum
from shared.src.enums.language_enums import LanguageEnum


class HomeTileTranslation(BaseModel):
    language: LanguageEnum


class BaseHomeTile(BaseModel):
    type: Literal[HomeTileEnum.BENEFITS, HomeTileEnum.NEWS, HomeTileEnum.EVENTS, HomeTileEnum.SPORTS, HomeTileEnum.ROOMFINDER, HomeTileEnum.WISHLIST, HomeTileEnum.FEEDBACK, HomeTileEnum.CINEMAS]
    size: int
    title: str
    description: str
    data: Any | None = None

    
class HomeTiles(RootModel):
    root: list[BaseHomeTile]
