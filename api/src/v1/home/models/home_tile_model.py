from typing import Any, Literal

from pydantic import BaseModel, RootModel

from shared.src.enums.home_tile_enums import HomeTileEnum
from shared.src.enums.language_enums import LanguageEnum


class HomeTileTranslation(BaseModel):
    language: LanguageEnum


class BaseHomeTile(BaseModel):
    type: Literal[HomeTileEnum.BENEFITS, HomeTileEnum.NEWS, HomeTileEnum.EVENTS, HomeTileEnum.SPORTS, HomeTileEnum.ROOMFINDER, HomeTileEnum.WISHLIST, HomeTileEnum.FEEDBACK, HomeTileEnum.CINEMAS, HomeTileEnum.TIMELINE, HomeTileEnum.LINKS]
    size: int
    title: str
    description: str | None = None
    data: Any | None = None

    
class HomeTiles(RootModel):
    root: list[BaseHomeTile]
