from typing import Any, Literal

from pydantic import BaseModel, Field, RootModel

from shared.src.enums.home_tile_enums import HomeTileEnum
from shared.src.enums.language_enums import LanguageEnum


class HomeTileTranslation(BaseModel):
    language: LanguageEnum


class BaseHomeTile(BaseModel):
    """
    Base model for all home tiles.
    """

    type: Literal[
        HomeTileEnum.BENEFITS,
        HomeTileEnum.NEWS,
        HomeTileEnum.EVENTS,
        HomeTileEnum.SPORTS,
        HomeTileEnum.ROOMFINDER,
        HomeTileEnum.WISHLIST,
        HomeTileEnum.FEEDBACK,
        HomeTileEnum.CINEMAS,
        HomeTileEnum.TIMELINE,
        HomeTileEnum.LINKS,
    ]
    size: int = Field(
        description="The size of the tile, 1 is the smallest and 3 is the largest",
        ge=1,
        le=3,
    )
    title: str = Field(
        description="The title of the tile",
    )
    description: str | None = Field(
        default=None,
        description="The description of the tile",
    )
    data: Any | None = Field(
        default=None,
        description="Optional data parameter for the tile. Can be used for deep linking, or other purposes.",
    )


class HomeTiles(RootModel):
    root: list[BaseHomeTile]
